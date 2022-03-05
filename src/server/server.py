# Server side

import os
import socket
import pickle
from pathlib import Path
from .loglib import Log
from .db import File_index, User_db


class Server:
    """Implementation of a Kryzbu server (Cryptographically Secure Storage)."""

    IP = "127.0.0.1"
    PORT = 60606
    BUFFER_SIZE = 4096 # TODO: defined on two seperate places (in client.py as well)
    SERVER_FOLDER = Path("server/_data/files/") # Universal Path object for multi OS path declaration


    @staticmethod
    def run():
        """Server's main loop for handling clients requests."""

        Server.init()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
            handle.bind((Server.IP, Server.PORT))

            while True:
                handle.listen(10)
                conn, addr = handle.accept()
                request = conn.recv(1024).decode()

                if 'UPLOAD' in request:
                    # Request to upload file, structure: 'UPLOAD FILENAME USERNAME'
                    _, file_name, user_name = request.split(';')
                    Server.recieve_file(file_name, user_name, conn)
                elif 'DOWNLOAD' in request:
                    # Request to download file, structure: 'DOWNLOAD FILENAME USERNAME'
                    _, file_name, user_name = request.split(';')
                    Server.serve_file(file_name, user_name, conn)
                elif 'REMOVE' in request:
                    # Request to delete file, structure: 'REMOVE FILENAME USERNAME'
                    _, file_name, user_name = request.split(';')
                    Server.remove_file(file_name, user_name, conn)
                elif 'LIST_DIR' in request:
                    # Request to list available file for download, structure: 'LIST_DIR'
                    Server.list_files(conn)
                else:
                    conn.send('UN-KNOWN request, use \{UPLOAD, DOWNLOAD, LIST_DIR\}'.encode())

                conn.close()


    @staticmethod
    def init() -> None:
        """Checks if required folder structure for server exists, any other initialization stuf should be here."""

        PATHS = (
        'server/_data/files/',
        'server/_data/logs/'
        )
        for path in PATHS:
            # Any missing parents of this path are created as needed, if folder already exists nothing happens
            Path(path).mkdir(parents=True, exist_ok=True)

        # Initiate file index
        File_index.init(Server.SERVER_FOLDER)
        
        #Initiate user database
        User_db.init()

        print('[*] Kryzbu server started successfully...')


    @staticmethod
    def recieve_file(file_name: str, user_name: str, conn: socket.socket):
        """Receive file from a client."""

        if User_db.name_exists(user_name):
            # User authenticated based on username
            conn.send("OK;Authenticated".encode())
            
            file_path = Server.SERVER_FOLDER / file_name

            with open(file_path, "wb") as f:
                while True:
                    bytes_read = conn.recv(Server.BUFFER_SIZE)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
            
            Log.event(Log.Event.UPLOAD, 0, [file_name, user_name])
            File_index.add(file_name, user_name)
        else:
            # User not-authenticated
            conn.send("ERROR;NotAuthenticated".encode())


    @staticmethod
    def serve_file(file_name: str, user_name: str, conn: socket.socket):
        """Send file to a client."""

        if User_db.name_exists(user_name):
            # User authenticated based on username
            file_path = os.path.join(Server.SERVER_FOLDER, file_name)

            if os.path.exists(file_path):
                # Inform client about authentication
                conn.send("OK;Authenticated".encode())
                
                # Send file info
                file_size = os.path.getsize(file_path)
                conn.send(f"{file_name};{file_size}".encode())

                # Send file
                with open(file_path, "rb") as f:
                    while True:
                        bytes_read = f.read(Server.BUFFER_SIZE)
                        if not bytes_read:
                            break
                        conn.send(bytes_read)

                Log.event(Log.Event.DOWNLOAD, 0, [file_name, user_name])
                File_index.download(file_name)
            else:
                # Requested file does NOT exist
                conn.send("ERROR;FileNotFoundError".encode())
        else:
            # User not-authenticated
            conn.send("ERROR;NotAuthenticatedError".encode())


    @staticmethod
    def remove_file(file_name: str, user_name: str, conn: socket.socket):
        """Remove file."""

        if User_db.name_exists(user_name):
            # User authenticated based on username
            file_path = os.path.join(Server.SERVER_FOLDER, file_name)

            if os.path.exists(file_path):
                # Inform client about authentication
                conn.send("OK;Authenticated".encode())

                os.remove(file_path)
                Log.event(Log.Event.DELETE, 0, [file_name, user_name])
                File_index.delete(file_name)
                conn.send(f"OK;FileDeleted;{file_name}".encode())
            else:
                # Requested file does NOT exist
                conn.send("ERROR;FileNotFoundError".encode())
        else:
            #User not_authenticated
            conn.send("ERROR;NotAuthenticatedError".encode())

    @staticmethod
    def list_files(conn: socket.socket):
        """Send available files for download."""
        
        conn.send(pickle.dumps(File_index.return_all()))
