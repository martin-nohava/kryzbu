# Client side

import os
import tqdm
import socket
import pickle

class Client:
    """Implementation of a Kryzbu client."""

    BUFFER_SIZE = 4096
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 60606


    @staticmethod

    def upload(file_path: str):
        """Upload file to a server."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((Client.SERVER_IP, Client.SERVER_PORT))
            except ConnectionRefusedError as e:
                print(e)
                print("Server probably isn't running!!!")
                exit(1)

            file_name = os.path.basename(file_path)

            # Send UPLOAD request
            client.send(f"UPLOAD;{file_name}".encode())

            # Initialize progress bar

            file_size = os.path.getsize(file_path)

            progress = tqdm.tqdm(range(file_size), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024)

            # Send file
            with open(file_path, "rb") as f:
                while True:
                    bytes_read = f.read(Client.BUFFER_SIZE)
                    if not bytes_read:
                        break
                    client.sendall(bytes_read)
                    progress.update(len(bytes_read))

            client.close()


    @staticmethod
    def download(file_name: str):
        """Download file from a server."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((Client.SERVER_IP, Client.SERVER_PORT))
            except ConnectionRefusedError as e:
                print(e)
                print("Server probably ins't running!!!")
                exit(1)

            # Send DOWNLOAD request
            client.send(f"DOWNLOAD;{file_name}".encode())

            # Receive aswer
            answer = client.recv(Client.BUFFER_SIZE).decode()
            if 'ERROR' in answer:
                print(f"File '{file_name}' does NOT exist")
                print("Available files:")
                Client.list_files()
                client.close()
                return
            else:
                file_name, file_size = answer.split(';')

            progress = tqdm.tqdm(range(int(file_size)), f"Receiving {file_name}", unit="B", unit_scale=True, unit_divisor=1024)

            # Receive file
            with open(str(os.path.join(os.path.expanduser('~/Downloads'), file_name)), "wb") as f:
                while True:
                    bytes_read = client.recv(Client.BUFFER_SIZE)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
                    progress.update(len(bytes_read))

            client.close()


    @staticmethod
    def list_files():
        """List stored files on server."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((Client.SERVER_IP, Client.SERVER_PORT))
            except ConnectionRefusedError as e:
                print(e)
                print("Server probably ins't running!!!")
                exit(1)

            # Send LIST_DIR request
            client.send(f"LIST_DIR".encode())

            # Receive available files
            list = pickle.loads(client.recv(1024))   # TODO: Potentional problem when files list is bigger than 1024b
            
            print ("{:<20} {:>1} {:<15} {:>1} {:<15} {:>1} {:<10}".format('File','|','Owner','|','Created','|','Downloads'))
            print ("{:–<65}".format('–'))
            for row in list:
                print ("{:<20} {:>1} {:<15} {:>1} {:<15} {:>1} {:<10}".format(row[0], '|', row[1], '|', row[2], '|', str(row[3])))
                #print(row[0] + ' ' + row[1] + ' ' + row[2] + ' ' + str(row[3]))


