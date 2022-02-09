import socket
from _thread import *

class ISMSocket:
    """
    Integrated sensor monitoring tool TCP/IP socket
    """
    def __init__(self, host, port, logging):
        self.logging = logging

        self.host = host
        self.port = port

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind((self.host, self.port))

        self.client_socket = None

    def listen(self):
        self.server_socket.listen()
        self.client_socket, addr = self.server_socket.accept()
        self.logging.info("Connected by", addr)

        while True:
            data = self.client_socket.recv(1024)

            if not data:
                break

            self.logging.info("Received from", addr, data.decode())
            self.client_socket.sendall(data)

    def close(self):
        self.client_socket.close()
        self.server_socket.close()
