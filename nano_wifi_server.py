import socket
import time 
import numpy as np
from PIL import Image
import random
import os
from trt_detector import TRTDetector
from utils.network import buff2numpy

CLASSES = ('person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
               'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
               'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
               'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe',
               'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
               'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat',
               'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
               'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
               'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
               'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
               'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
               'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
               'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock',
               'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush')

class NanoServer:
    def __init__(self, detector,
                 TCP_IP='0.0.0.0', TCP_PORT=8584,
                 buffer_size=730
    ):
        self.detector = detector
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.buffer_size = buffer_size
        #self.num_bytes = np.prod(self.detector.input_shape)
        self.target_bytes = 8*28*28
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))

    @property
    def randbytes(self):
        return open("/dev/random","rb").read(4)

    def run(self):
        print("nano server started")
        self.sock.listen(5)
        client, addr = self.sock.accept()
        print("Connected:", addr)
        client.send(self.randbytes)
        prev_time = 0
        cur_time = 0
        counter = 0
        total_size = 0
        data = b''
        start = False
        count = 0
        new_packet = False

        while True:
            content = client.recv(self.buffer_size)
            if len(content) == 0:
                continue
            if int(content[1]) == 0:
                new_packet = True
            if new_packet:
                client.send(self.randbytes)
                new_packet = False
            if int(content[1]) != 0 and not start:
                continue
            elif int(content[1]) == 0:
                start = True
            
            packetData = content[4:]
            real_length = int(content[2]) << 8 | int(content[3])
            total_size += real_length
            data = data + packetData[:real_length]
            if total_size == self.target_bytes:
                if prev_time == 0:
                    prev_time = time.time() * 10**9
                else:
                    cur_time = time.time() * 10**9
                    print("Bw: %.3f KBps (%.1f ms)" % (total_size / ((cur_time - prev_time) / 1000 / 1000), (cur_time - prev_time) / 1000 / 1000))
                    prev_time = cur_time
                
                channels = buff2numpy(data, dtype=np.int8)
                channels = channels.reshape(8, 28, 28)
                channels = channels.astype(np.float32)
                channels = (channels - -128) * 0.02352941
                
                z_channels = np.zeros([32-8, 28, 28], dtype=np.float32)
                channels = np.concatenate([channels, z_channels], axis=0)
                channels = np.expand_dims(channels, axis=0) #1 C H W
                dets = self.detector.detect(channels)
                # for det in dets:
                    # print(det, CLASSES[det[-1]])
                count += 1
                data = b''
                start = False
                total_size = 0



                        
if __name__ == '__main__':
    detector = TRTDetector('/root/gap_runner/models/tflite_models/suffix.trt')
    server = NanoServer(detector)
    while True:
        server.run()
