import time
import socket
import numpy as np
from pickle import dumps, loads
import subprocess
from utils.network import recvall
from trt_detector import TRTDetector

class NanoServer:
    def __init__(self, detector,
                 TCP_IP='0.0.0.0', TCP_PORT=5001,
                 buffer_size=1024,
    ):
        self.detector = detector
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.buffer_size = buffer_size
        self.num_bytes = np.prod(self.detector.input_shape)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))

    def run(self):
        print("nano server started")
        
        self.sock.listen()
        conn, addr = self.sock.accept()
        while True:
            message = recvall(self.sock, self.num_bytes, self.buffer_size)
            if not message:
                break

            channels = loads(message) 
            
            dets = self.detector.detect(channels)
            buff = dumps(dets)
            conn.sendall(buff)
            
if __name__ == '__main__':
    detector = TRTDetector('/root/gap_runner/suffix.trt')
    server = NanoServer(detector)
    while True:
        server.run()
