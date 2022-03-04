# Server side

import os
import socket
import pickle
from pathlib import Path
from .loglib import Log
from .db import File_index


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
                    # Request to upload file, structure: 'UPLOAD FILENAME'
                    _, file_name = request.split(';')
                    Server.recieve_file(file_name, conn)
                elif 'DOWNLOAD' in request:
                    # Request to download file, structure: 'DOWNLOAD FILENAME'
                    _, file_name = request.split(';')
                    Server.serve_file(file_name, conn)
                elif 'REMOVE' in request:
                    # Request to delete file, structure: 'REMOVE FILENAME'
                    _, file_name = request.split(';')
                    Server.remove_file(file_name, conn)
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
        

    @staticmethod
    def recieve_file(file_name: str, conn: socket.socket):
        """Receive file from a client."""

        file_path = Server.SERVER_FOLDER / file_name # Prepend storage path

        with open(file_path, "wb") as f:
            while True:
                bytes_read = conn.recv(Server.BUFFER_SIZE)
                if not bytes_read:
                    break
                f.write(bytes_read)
        # Logs event type 'UPLOAD', with sucess 0, and payload with file name
        Log.event('UPLOAD', 0, [file_name])
        File_index.add(file_name)


    @staticmethod
    def serve_file(file_name: str, conn: socket.socket):
        """Send file to a client."""

        file_path = os.path.join(Server.SERVER_FOLDER, file_name)

        if os.path.exists(file_path):
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

            Log.event('DOWNLOAD', 0, [file_name])
            File_index.download(file_name)
        else:
            # Requested file does NOT exist
            conn.send("ERROR;FILE_NOT_FOUND".encode())


    @staticmethod
    def remove_file(file_name: str, conn: socket.socket):
        """Remove file."""

        file_path = os.path.join(Server.SERVER_FOLDER, file_name)

        if os.path.exists(file_path):
            os.remove(file_path)
            Log.event('DELETE', 0, [file_name])
            File_index.delete(file_name)
            conn.send(f"SUCCESS;fileDeleted;{file_name}".encode())
        else:
            # Requested file does NOT exist
            conn.send("ERROR;FILE_NOT_FOUND".encode())


    @staticmethod
    def list_files(conn: socket.socket):
        """Send available files for download."""
        
        conn.send(pickle.dumps(File_index.return_all()))
