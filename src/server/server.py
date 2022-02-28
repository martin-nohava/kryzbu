# Server side

import socket
import os
import tqdm
import os.path
import time


class Server:
    """Implementation of a Kryzbu server (Cryptographically Secure Storage)."""

    IP = "127.0.0.1"
    PORT = 60606
    BUFFER_SIZE = 4096
    SERVER_FOLDER = os.getenv('APPDATA') + '\\KryzbuServer\\' # Where to save
    if os.path.exists('C:\\Users\\micha\\AppData\\Roaming' +'\\KryzbuServer\\') == False:
        os.mkdir('C:\\Users\\micha\\AppData\\Roaming' +'\\KryzbuServer\\')





    SEPARATOR = " " #TODO: je to na dvo mistech

    @staticmethod
    def recieve_file():
        s = socket.socket()
        s.bind((Server.IP, Server.PORT))
        s.listen(10)
        client_socket, address = s.accept()
        received = client_socket.recv(Server.BUFFER_SIZE).decode()
        filename, filesize = received.split(Server.SEPARATOR)
        file_path = os.path.join(Server.SERVER_FOLDER, filename)
        print(filename)
        progress = tqdm.tqdm(range(int(filesize)), f"Receiving {file_path}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(file_path, "wb") as f:
            while True:
                bytes_read = client_socket.recv(Server.BUFFER_SIZE)
                if not bytes_read:
                    break
                f.write(bytes_read)
                progress.update(len(bytes_read))
        client_socket.close()
        s.close()


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
