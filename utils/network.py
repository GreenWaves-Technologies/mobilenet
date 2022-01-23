import socket
from multiprocessing import Queue, Process

def recvall(sock, target_size=4096, buffer_size=4096):
    data = b''
    while True:
        part = sock.recv(buffer_size)
        if not part:
            return None
        data += part
        if len(data) == target_size:
            break
    return data

class QClient:
    def __init__(self, server_ip='127.0.0.1', server_port=5000, buffer_size=4096):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = buffer_size
        self.Qin = Queue()
        self.Qout = Queue()
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_ip,  self.server_port))
        self.process = Process(target=self.run, args=())
        self.process.start()
        
    def run(self):
        while True:
            message, num_bytes = self.Qin.get()
            self.sock.sendall(message)
            buff = recvall(self.sock, num_bytes, self.buffer_size)
            self.Qout.put(buff)
   
    def put(self, x):
        return self.Qin.put(x)

    def get(self):
        return self.Qout.get()
