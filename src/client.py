# Client side

import socket

def example_comm_c():
    '''Send b"Hello, word" to localhost:50000 over TCP.'''

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 50000))
    client.sendall(b'Hello, world')
    client.close()

if __name__ == '__main__':
    example_comm_c()
