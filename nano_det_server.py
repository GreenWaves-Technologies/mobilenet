import socket
import time 
import numpy as np
import cv2
# from PIL import Image
import random
import os
from trt_detector import TRTDetector
from utils.network import buff2numpy
import asyncio
import websockets
import queue
from threading import Thread
from utils.inference import draw_dets

class NanoServer:
    def __init__(self, detector,
                 TCP_IP='0.0.0.0', TCP_PORT=8584,
                 buffer_size=730
    ):
        self.detector = detector
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.buffer_size = buffer_size
        self.target_bytes = 8*28*28 + 224*224
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))

    @property
    def randbytes(self):
        return open("/dev/random","rb").read(4)

    # def run(self, Q):
    def run(self):
        print("nano detection server started")
        self.sock.listen(5)
        client, addr = self.sock.accept()
        print("Connected:", addr) 
        client.send(self.randbytes)
        counter = 0
        total_size = 0
        data = b''
        start = False
        count = 0
        new_packet = False

        # fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        # out = cv2.VideoWriter('/root/gap_runner/vid.mp4', fourcc, 30, (224, 224))

        # vid = cv2.VideoWriter('/root/gap_runner/vid.avi', cv2.VideoWriter_fourcc(*'MJPG'), 30, (224, 224))
        while True:
            start_time = time.time()
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
                num_pixels = 224*224
                img = buff2numpy(data[0:num_pixels], dtype=np.uint8)
                img = img.reshape(224, 224)
                channels = buff2numpy(data[num_pixels:], dtype=np.int8)
                channels = channels.reshape(8, 28, 28)
                channels = channels.astype(np.float32)
                channels = (channels - -128) * 0.02352941
                
                z_channels = np.zeros([32-8, 28, 28], dtype=np.float32)
                channels = np.concatenate([channels, z_channels], axis=0)
                channels = np.expand_dims(channels, axis=0) #1 C H W
                dets = self.detector.detect(channels)
                img = draw_dets(img, dets)
                
                # vid.write(img) 
                # frame_num = str(count).zfill(5)
                cv2.imwrite('/root/gap_runner/htdocs/imgs/frame.png', img)
                for i in range(8):
                    h = channels[0, i] # H W
                    h = h / h.max() #note that h \in [0, 6] from ReLU6
                    h = h * 255
                    h = h.astype(np.uint8)
                    fname = '/root/gap_runner/htdocs/imgs/h%d.png' % (i + 1)
                    cv2.imwrite(fname, h)

                # if Q.qsize() == 0: 
                    # Q.put_nowait(count)

                count += 1
                data = b''
                start = False
                total_size = 0
                print(count, time.time() - start_time)

def start_websocket_loop(loop, server):
    loop.run_until_complete(server)
    loop.run_forever()

async def image_notify(websocket, path, queue):
    while True:
        count = queue.get()
        await websocket.send("count %d" % count)
               
if __name__ == '__main__':
    detector = TRTDetector('/root/gap_runner/models/tflite_models/suffix.trt')
    server = NanoServer(detector)

    # websocket_loop = asyncio.new_event_loop()
    
    # imgqueue = queue.Queue()
    
    # start_server = websockets.serve(
        # lambda ws, p : image_notify(ws,p,imgqueue),
        # 'localhost', 8111, loop=websocket_loop
    # )

    # t1 = Thread(target=start_websocket_loop, args=(websocket_loop, start_server))
    # t1.start()
    
    # server.run(imgqueue)
    server.run()
    
    
    # t2 = Thread(target=server.run, args=(imgqueue,))
    # t2.start()

    # while True:
        # server.run()
