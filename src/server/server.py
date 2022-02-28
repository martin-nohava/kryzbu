# Server side

import socket
import os
import tqdm
import os.path
from pathlib import Path 


class Server:
    """Implementation of a Kryzbu server (Cryptographically Secure Storage)."""

    IP = "127.0.0.1"
    PORT = 60606
    BUFFER_SIZE = 4096 # TODO: defined on two seperate places (in client.py as well)
    SERVER_FOLDER = Path("server/_data/files/") # Universal Path object for multi OS path declaration


    @staticmethod
    def recieve_file():
        """Receive file from a client."""

        if os.path.exists(Server.SERVER_FOLDER) == False:
            os.mkdir(Server.SERVER_FOLDER)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((Server.IP, Server.PORT))
            server.listen(10)
            client_connection, address = server.accept()

            received = client_connection.recv(Server.BUFFER_SIZE).decode()
            filename, filesize = received.split()
            file_path = Server.SERVER_FOLDER / os.path.basename(filename) # Prepend storage path

            progress = tqdm.tqdm(range(int(filesize)), f"Receiving {file_path}", unit="B", unit_scale=True, unit_divisor=1024)

            with open(file_path, "wb") as f:
                while True:
                    bytes_read = client_connection.recv(Server.BUFFER_SIZE)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
                    progress.update(len(bytes_read))


    def serve_file():
        """Send file to a client."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((Server.IP, Server.PORT))
            server.listen(1)
            client_connection, addr = server.accept()

            # TODO: comunicate with client which file should be downloaded
            file_name = 'text.txt'
            # ------------------------------------------------------------

            filesize = os.path.getsize(file_name)
            client_connection.send(f"{file_name} {filesize}".encode())

            progress = tqdm.tqdm(range(filesize), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024)

            with open(file_name, "rb") as f:
                while True:
                    bytes_read = f.read(Server.BUFFER_SIZE)
                    if not bytes_read:
                        break
                    client_connection.send(bytes_read)
                    progress.update(len(bytes_read))


    @staticmethod
    def example_comm():
            '''Receive 1024b block from TCP stream'''

            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((Server.IP, Server.PORT))

            server.listen(1)
            conn, addr = server.accept()

            data = conn.recv(1024)

            server.close()

            print(data)
