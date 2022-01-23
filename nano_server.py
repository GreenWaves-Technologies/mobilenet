import time
import socket
import numpy as np
from pickle import dumps, loads
import subprocess
from utils.network import recvall
from trt_detector import TRTDetector

class NanoServer:
    def __init__(self, detector,
                 TCP_IP='0.0.0.0', TCP_PORT=5000,
                 BUFFER_SIZE=1024,
                 HID_W=28, HID_H=28, MAX_HIDS=8
    ):
        self.detector = detector
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.BUFFER_SIZE = BUFFER_SIZE
        self.HID_W = HID_W
        self.HID_H = HID_H
        self.MAX_HIDS = MAX_HIDS
        self.SPATIAL_DIM = HID_H * HID_W
        self.num_bytes = HID_W * HID_H * MAX_HIDS 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))

    def run(self):
        print("nano server started")
        
        self.sock.listen()
        conn, addr = self.sock.accept()
        while True:
            message = recvall(self.sock, self.num_bytes, self.BUFFER_SIZE)
            if not message:
                break

            channels = loads(message) 
            
            dets = self.detector.detect(channels)
            buff = dumps(dets)
            conn.sendall(buff)
            
if __name__ == '__main__':
    detector = TRTDetector('/root/gap_runner/suffix.trt')
    print(detector.input_shape)
    # server = NanoServer(detector)
    # while True:
        # server.run()
