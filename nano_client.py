import os
import time
import numpy as np
import socket 
from pickle import dumps, loads
from trt_detector import TRTDetector
from utils.network import QClient, buff2numpy
import json
import pickle

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


class NanoClient:
    def __init__(self, gap_client, detector,
            TCP_IP='127.0.0.1', TCP_PORT=5000, 
            IMG_W=224, IMG_H=224, 
            HID_W=28, HID_H=28,
            MIN_HIDS=1, MAX_HIDS=32,
            HID_GRID=6, SKIP_HID=2,
            num_dets=50
    ):
        self.gap_client = gap_client
        self.detector = detector
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.IMG_W = IMG_W
        self.IMG_H = IMG_H
        self.HID_W = HID_W
        self.HID_H = HID_H
        self.SPATIAL_DIM = self.HID_H * self.HID_W
        self.MIN_HIDS = MIN_HIDS
        self.MAX_HIDS = MAX_HIDS
        self.SKIP_HID = SKIP_HID
        self.HID_GRID = HID_GRID
        self.num_dets = num_dets
        self.time_bytes = 12
        self.frame_count = 0
        self.path = os.path.join(os.environ['HOME'], 'record/')
    
    def run(self):
        start = time.time()
        include_img = False
        num_channels = 32
        
        img_bytes = self.IMG_W * self.IMG_H if include_img else 0
        hid_bytes = self.SPATIAL_DIM * num_channels
        num_bytes = self.time_bytes + hid_bytes
        num_bytes += img_bytes

        message = dumps([include_img, num_channels])
        self.gap_client.put((message, num_bytes))
        buff = self.gap_client.get()
        
        img = buff[0:img_bytes]
        hid = buff[img_bytes:img_bytes+hid_bytes]
        time_vals = buff[img_bytes+hid_bytes:]
        
        img = buff2numpy(img, dtype=np.uint8)
        hid = buff2numpy(hid, dtype=np.int8)
        time_vals = buff2numpy(time_vals, dtype=np.uint32) * 10**-6
        
        dets = None
        if num_channels > 0:
            hid = hid.reshape(-1, self.HID_H, self.HID_W)
            byte_hid = hid
            hid = hid.astype(np.float32)
            hid = (hid - -128) * 0.02352941 #unquantize
            
            num_zeros = self.MAX_HIDS - len(hid)
            z_channels = np.zeros((num_zeros, self.HID_H, self.HID_W),
                    dtype=hid.dtype)
            hid = np.concatenate([hid, z_channels], axis=0)
            hid = hid.reshape(1, *hid.shape)
            print(hid.shape)


            dets = self.detector.detect(hid)

        out = {
            'img': img,
            'hid': byte_hid,
            'dets': dets
        }
        # fname = '%s/frame_%05.0f.pkl' % (self.path, self.frame_count)
        # with open(fname, 'wb') as f:
            # pickle.dump(out, f)
        self.frame_count += 1
        print(time.time() - start)

        
if __name__ == '__main__':
    gap_client = QClient(
        server_ip='192.168.0.105',
        server_port=5000,
        buffer_size=4096
    )
        
    detector = TRTDetector('/root/gap_runner/models/tflite_models/suffix.trt')
    client = NanoClient(gap_client, detector)
    while True:
        client.run()
