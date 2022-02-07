import time
import socket
import numpy as np
from pickle import dumps, loads
import subprocess
# from utils.network import recvall
from trt_detector import TRTDetector
from utils.network import buff2numpy

def recvall(sock, target_size=4096, buffer_size=4096):
    data = b''
    print(len(data), end=' ')
    while True:
        part = sock.recv(buffer_size)
        if not part:
            return None
        data += part
        print(len(data), end=' ')
        if len(data) == target_size:
            break
    return data


class NanoServer:
    def __init__(self, 
                 TCP_IP='0.0.0.0', TCP_PORT=80,
                 buffer_size=32,
    ):
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.buffer_size = buffer_size
        self.num_bytes = 32*5
        # self.num_bytes = 8*28*28
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))

    def run(self):
        print("nano server started")
        
        self.sock.listen()
        conn, addr = self.sock.accept()
        print(addr)
        while True:
            message = recvall(conn, self.num_bytes, self.buffer_size)
            if not message:
                break

            print(message)
            print(len(message))
            
            # print('nano: got message of len', len(message))
            # channels = buff2numpy(message, dtype=np.int8)
            # channels = channels.reshape(8, 28, 28)
            # channels = channels.astype(np.float32)
            # channels = (channels - -128) * 0.02352941
            
            # z_channels = np.zeros([32-8, 28, 28], dtype=np.float32)
            # channels = np.concatenate([channels, z_channels], axis=0)
            # channels = np.expand_dims(channels, axis=0) #1 C H W
            # dets = self.detector.detect(channels)
            # for det in dets:
                # print(det, CLASSES[det[-1]])
            # buff = dumps(dets)
            # print('nano: sending bytes', len(buff))
            # conn.sendall(buff)
            
if __name__ == '__main__':
    server = NanoServer()
    while True:
        server.run()
