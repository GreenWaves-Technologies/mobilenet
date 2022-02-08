import time
import socket
import numpy as np
from pickle import dumps, loads
import subprocess
# from utils.network import recvall
from trt_detector import TRTDetector
from utils.network import buff2numpy

def recvall(conn, target_size=4096, buffer_size=4096):
    data = b''
    while True:
        part = conn.recv(buffer_size)
        if not part:
            return None
        data += part
        if len(data) >= target_size:
            break
    return data


class NanoServer:
    def __init__(self, 
                 TCP_IP='0.0.0.0', TCP_PORT=80,
                 buffer_size=1000,
    ):
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.buffer_size = buffer_size
        self.num_bytes = 250
        # self.num_bytes = 8*28*28
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        self.sock.settimeout(10)

    def run(self):
        print("nano server started")
        self.sock.listen()
        conn, addr = self.sock.accept()
        total_len = 0
        print(addr)
        data = b''
        seq_num = 0
        packet_size = 1460
        while len(data) != 1000 * packet_size:
            while True:
                part = conn.recv(packet_size)
                data += part
                if len(data) >= packet_size:
                    message = data[0:packet_size]
                    data = data[packet_size:]
                    total_len += len(message)
                    remote_seq_num = message[0]
                    assert remote_seq_num == seq_num
                    seq_num += 1
                    seq_num = seq_num % 256
                    if total_len == 1000 * packet_size:
                        print(message[0], len(message), total_len)
                    break
            
                        
if __name__ == '__main__':
    server = NanoServer()
    while True:
        server.run()
