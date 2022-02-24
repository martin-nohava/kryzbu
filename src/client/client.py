# Client side

import socket
import asyncio
import os

class Client:
    """Implementation of a Kryzbu client."""

    @staticmethod
    def send_file():
        
        SEPARATOR = "\\"
        BUFFER_SIZE = 4096

        s = socket.socket()
        host = "127.0.0.1"
        port = 60606
        print(f"[+] Connecting to {host}:{port}")
        s.connect((host, port))
        print("[+] Connected to ", host)
        filename = input('Enter file name: ')
        filesize = os.path.getsize(filename)
        s.send(f"{filename}{SEPARATOR}{filesize}".encode())

        #progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                s.sendall(bytes_read)
                #progress.update(len(bytes_read))
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
    Client.send_file()
