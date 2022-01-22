import time
import socket
from pickle import dumps, loads


def recvall(sock, TARGET_SIZE=4096, BUFFER_SIZE=4096):
    data = b''
    while True:
        part = sock.recv(BUFFER_SIZE)
        data += part
        if len(data) == TARGET_SIZE:
            break
    return data


class QClient:
    def __init__(self, sock, Qin, Qout, BUFFER_SIZE=4096):
        self.sock = sock
        self.Qin = Qin
        self.Qout = Qout
        self.BUFFER_SIZE = BUFFER_SIZE
        
    def run(self):
        # while self.Qin.qsize() > 0:
        message, num_bytes = self.Qin.get() 
        print('qin get')
        self.sock.send(message)
        print('message sent')
        buff = recvall(self.sock, num_bytes, self.BUFFER_SIZE)
        print('respose recv')
        self.Qout.put(buff)
        print('qout put')
            
        
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
