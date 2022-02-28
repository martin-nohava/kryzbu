# Server side

import socket
import os
import tqdm

class Server:
    """Implementation of a Kryzbu server (Cryptographically Secure Storage)."""

    IP = "127.0.0.1"
    PORT = 60606
    BUFFER_SIZE = 4096
    SEPARATOR = "\\"

    @staticmethod
    def recieve_file():     
        s = socket.socket()
        s.bind((Server.IP, Server.PORT))
        s.listen(10)
        print(f"[*] Listening as {Server.IP}:{Server.PORT}")
        client_socket, address = s.accept()
        print(f"[+] {address} is connecting...")
        received = client_socket.recv(Server.BUFFER_SIZE).decode()
        filename, filesize = received.split(Server.SEPARATOR)
        filename = os.path.abspath("T:\Dokumenty\Programování\Python\kryzbu\\" + filename) #<--------------------------------- Where to Save the File -----------
        filesize = int(filesize)
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            print("Saving to: " + filename)
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
    

if __name__ == '__main__':
    while True:
        Server.recieve_file()
