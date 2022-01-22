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
            message, num_bytes = self.get() 
            self.sock.send(message)
            buff = recvall(self.sock, num_bytes, self.BUFFER_SIZE)
            self.put(buff)
    
    def put(self, x):
        self.Qin.put(x)

    def get(self):
        return self.Qout.get()
            
        
# if __name__ == '__main__':
    # TCP_IP = '192.168.0.124'
    # TCP_PORT = 5000
    # BUFFER_SIZE = 1024
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.connect((TCP_IP, TCP_PORT))
    # root = Tk.Tk()
    # gui = GUI(root, sock)
    # root.after(200, gui.do_refresh) 
    # root.mainloop()
