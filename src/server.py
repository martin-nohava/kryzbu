# Server side

import socket


def example_comm_s():
    "Receive 1024b block from TCP stream at port 50000."

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 50000))

    server.listen(1)
    conn, addr = server.accept()

    data = conn.recv(1024)

    server.close()

    print(data)

if __name__ == '__main__':
    example_comm_s()
