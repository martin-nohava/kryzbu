# Client side

import socket
import os
import tqdm


class Client:
    """Implementation of a Kryzbu client."""

    BUFFER_SIZE = 4096
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 60606

    @staticmethod
    def upload(file_name: str):
        """Upload file to a server."""

        with socket.socket() as client:
            try:
                client.connect((Client.SERVER_IP, Client.SERVER_PORT))
            except ConnectionRefusedError as e:
                print(e)
                print("Server probably isn't running!!!")
                exit(1)

            filesize = os.path.getsize(file_name)
            client.send(f"{os.path.split(file_name)[1]} {filesize}".encode())

            progress = tqdm.tqdm(range(filesize), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(file_name, "rb") as f:
                while True:
                    bytes_read = f.read(Client.BUFFER_SIZE)
                    if not bytes_read:
                        break
                    client.sendall(bytes_read)
                    progress.update(len(bytes_read))


    def download(file_name: str):
        """Download file from a server."""

        with socket.socket() as client:
            try:
                client.connect((Client.SERVER_IP, Client.SERVER_PORT))
            except ConnectionRefusedError as e:
                print(e)
                print("Server probably ins't running!!!")
                exit(1)

            received = client.recv(Client.BUFFER_SIZE).decode()
            file_name, file_size = received.split()

            progress = tqdm.tqdm(range(int(file_size)), f"Receiving {file_name}", unit="B", unit_scale=True, unit_divisor=1024)

            with open(file_name, "wb") as f:
                while True:
                    bytes_read = client.recv(Client.BUFFER_SIZE)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
                    progress.update(len(bytes_read))


    @staticmethod
    def open_n_hold():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
            handle.connect(('localhost', 60606))


    @staticmethod
    async def example_comm():
        '''Send b"Hello, word" to localhost:50000 over TCP.'''

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 60606))
        client.sendall(b'Hello, world')
        client.close()

if __name__ == '__main__':
    Client.send_file('text.txt')
