# Server side

import socket
import os


class Server:
    """Implementation of a Kryzbu server (Cryptographically Secure Storage)."""

    # Static variables
    IP_ADDR: str = None
    PORT: int = None

    # List of opened connections
    open_conns = [] 

    def __init__(self, ip_addr: str = 'localhost'):
        """Constructor initialize IP_ADDR (127.0.0.1 by default) and PORT (60606 by default) and
        bind TCP connection, but doesn't start listenning."""

        Server.IP_ADDR = ip_addr

        self.server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def listen_for_connection(self, queue_size: int = 1, port: int = 60606):
        """Listen for TCP connections on specified port. Incoming connections
        are accepted as long as there is space in queue. Accepted connections
        are added to open_conns list.

        Parameters:
            queue_size (int): Size of queue for incoming connections (default 1).
            port (int): Port to listen on (default 60606).

        Returns:
            (socket): socket with accepted connection
            (str): IPv4 address (conn, src_addr)."""
        Server.PORT = port
        self.server.bind((Server.IP_ADDR, Server.PORT))  # TODO: Can throw exceptions
        self.server.listen(queue_size)
        conn, src_addr = self.server.accept()
        return conn, src_addr


    def close_connection(self, connection: socket.socket):
        """Close specified TCP connection.
        
        Parameters:
            connection (socket): Connection to close."""
        connection.close()

    
    @staticmethod
    def recieve_file():
        SERVER_HOST = "127.0.0.1"
        SERVER_PORT = 60606
        BUFFER_SIZE = 4096
        SEPARATOR = "\\"

        s = socket.socket()
        s.bind((SERVER_HOST, SERVER_PORT))
        s.listen(10)
        print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
        print("Waiting for the client to connect... ")
        client_socket, address = s.accept()
        print(f"[+] {address} is connected.")
        received = client_socket.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        filename = os.path.basename(filename)
        filesize = int(filesize)
        #progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            while True:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    break
                f.write(bytes_read)
                #progress.update(len(bytes_read))
        client_socket.close()
        s.close()


    @staticmethod
    def example_comm():
            '''Receive 1024b block from TCP stream at port 50000.'''

            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(('localhost', 50000))

            server.listen(1)
            conn, addr = server.accept()

            data = conn.recv(1024)

            server.close()

            print(data)
    

if __name__ == '__main__':
    Server.recieve_file()
