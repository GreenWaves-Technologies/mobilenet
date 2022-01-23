from multiprocessing import Queue

def recvall(sock, target_size=4096, buffer_size=4096):
    data = b''
    while True:
        part = sock.recv(buffer_size)
        data += part
        if len(data) == target_size:
            break
    return data

class QClient:
    def __init__(self, sock, buffer_size=4096):
        self.sock = sock
        self.Qin = Queue()
        self.Qout = Queue()
        self.buffer_size = buffer_size
        
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
