# Server side

import os
import socket
import pickle
from pathlib import Path
from .loglib import Log
from .db import File_index
from os.path import exists

class Server:
    """Implementation of a Kryzbu server (Cryptographically Secure Storage)."""

    IP = "127.0.0.1"
    PORT = 60606
    BUFFER_SIZE = 4096 # TODO: defined on two seperate places (in client.py as well)
    SERVER_FOLDER = Path("server/_data/files/") # Universal Path object for multi OS path declaration


    @staticmethod
    def run():
        """Server's main loop for handling clients requests."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
            handle.bind((Server.IP, Server.PORT))

            while True:
                handle.listen(10)
                conn, addr = handle.accept()
                request = conn.recv(1024).decode()

                if 'UPLOAD' in request:
                    # Request to upload file structure: 'UPLOAD FILENAME'
                    _, file_name = request.split(';')
                    Server.recieve_file(file_name, conn)
                elif 'DOWNLOAD' in request:
                    # Request to download file structure: 'DOWNLOAD FILENAME'
                    _, file_name = request.split(';')
                    Server.serve_file(file_name, conn)
                elif 'LIST_DIR' in request:
                    # Request to list available file for download structure: 'LIST_DIR'
                    Server.list_files(conn)
                else:
                    conn.send('UN-KNOWN command, use \{UPLOAD, DOWNLOAD, LIST_DIR\}'.encode())

                conn.close()


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

    @staticmethod
    def list_files(conn: socket.socket):
        """Send available files for download."""

        files = os.listdir(Server.SERVER_FOLDER)
        conn.send(pickle.dumps(files))
