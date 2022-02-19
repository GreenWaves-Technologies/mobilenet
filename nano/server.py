import socket
import time 
import numpy as np
import cv2
from trt_detector import TRTDetector
from network import buff2numpy
from inference import draw_dets, write_dets

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

    def run(self):
        print("detection server waiting for TCP conntection...")
        self.sock.listen(5)
        client, addr = self.sock.accept()
        print("connected to client at %s" % addr[0]) 
        client.send(self.randbytes)
        counter = 0
        total_size = 0
        data = b''
        start = False
        count = 0
        new_packet = False

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
                img = np.stack([img] * 3, axis=-1) #convert to "color"
                channels = buff2numpy(data[num_pixels:], dtype=np.int8)
                channels = channels.reshape(8, 28, 28)
                channels = channels.astype(np.float32)
                channels = (channels - -128) * 0.02352941
                
                z_channels = np.zeros([32-8, 28, 28], dtype=np.float32)
                channels = np.concatenate([channels, z_channels], axis=0)
                channels = np.expand_dims(channels, axis=0) #1 C H W
                dets = self.detector.detect(channels)
                img = draw_dets(img, dets)
               

                cv2.imwrite('/root/gap_runner/web/htdocs/imgs/frame.jpg', img)
                for i in range(8):
                    h = channels[0, i] # H W
                    h = h / h.max() #note that h \in [0, 6] from ReLU6
                    h = h * 255
                    h = h.astype(np.uint8)
                    h = cv2.applyColorMap(h, cv2.COLORMAP_JET)
                    fname = '/root/gap_runner/web/htdocs/imgs/h%d.png' % (i + 1)
                    cv2.imwrite(fname, h)
                
                fname = '/root/gap_runner/web/htdocs/imgs/dets.json'
                write_dets(dets, fname, count) #write to json

                count += 1
                data = b''
                start = False
                total_size = 0
                time_diff = time.time() - start_time
                print('processed detection %d in %d ms' % (count, time_diff*1000))
               
if __name__ == '__main__':
    print("booting up nano detection server")
    detector = TRTDetector('/root/gap_runner/nano/suffix.trt')
    print("TRT detector suffix opened")
    server = NanoServer(detector)
    while True:
        server.run()
