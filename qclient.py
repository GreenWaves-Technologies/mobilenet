import time
import socket
from pickle import dumps, loads
from multiprocessing import Queue

def recvall(sock, TARGET_SIZE=4096, BUFFER_SIZE=4096):
    data = b''
    while True:
        part = sock.recv(BUFFER_SIZE)
        data += part
        if len(data) == TARGET_SIZE:
            break
    return data


class QClient:
    def __init__(self, sock, BUFFER_SIZE=4096):
        self.sock = sock
        self.Qin = Queue()
        self.Qout = Queue()
        self.BUFFER_SIZE = BUFFER_SIZE
        
    def run(self):
        while True:
            message, num_bytes = self.Qin.get()
            self.sock.sendall(message)
            buff = recvall(self.sock, num_bytes, self.BUFFER_SIZE)
            self.Qout.put(buff)
   
    def put(self, x):
        self.Qin.put(x)

    def get(self):
        return self.Qout.get()
