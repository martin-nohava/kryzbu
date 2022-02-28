# Client side

from logging import exception
import socket
import asyncio
import os
import tqdm

class Client:
    """Implementation of a Kryzbu client."""

    @staticmethod
    def send_file(file_name: str):
        """Send file to a server."""
        SEPARATOR = " "
        BUFFER_SIZE = 4096
        host = "127.0.0.1"
        port = 60606

        s = socket.socket()
        try:
            s.connect((host, port))
        except ConnectionRefusedError as e:
            print(e)
            print("Server probably isn't running!!!")
            exit(1)
        filesize = os.path.getsize(file_name)
        s.send(f"{file_name}{SEPARATOR}{filesize}".encode())

        progress = tqdm.tqdm(range(filesize), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(file_name, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                s.sendall(bytes_read)
                progress.update(len(bytes_read))
        s.close()

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
