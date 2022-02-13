import socket
import time 
import numpy as np
from PIL import Image
import random
import os

if not os.path.exists('./test'):
    os.mkdir('./test')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 8584))
s.listen(5)                 
 
prev_time = 0
cur_time = 0
counter = 0
total_size = 0
data = b''
start = False
count = 0
new_packet = False
while True:
    client, addr = s.accept()
    print("Connected:", addr)
    client.send(random.randbytes(4))
    while True:
        content = client.recv(730)
        if len(content) == 0:
            continue
        
        if int(content[1]) == 0:
            new_packet = True

        # print("Index:{}".format(int(content[1])))
        if new_packet:
            # client.send(b'\x01\x02\x03\x04')
            client.send(random.randbytes(4))
            # print("Send Commands")
            new_packet = False
        if int(content[1]) != 0 and not start:
            continue
        elif int(content[1]) == 0:
            start = True
        # for b in content:
        #     print(b, end = " ", flush=True)
        packetData = content[4:]
        real_length = int(content[2]) << 8 | int(content[3])
        total_size += real_length
        print("Index:{}".format(int(content[1])))
        # print("Packet Length:{}/{} - {}".format(real_length, total_size, len(packetData[:real_length])))
        data = data + packetData[:real_length]
        
        if total_size == 240 * 320:
            if prev_time == 0:
                prev_time = time.time_ns()
            else:
                cur_time = time.time_ns()
                print("Bw: %.3f KBps (%.1f ms)" % (total_size / ((cur_time - prev_time) / 1000 / 1000), (cur_time - prev_time) / 1000 / 1000))
                prev_time = cur_time
            total_size = 0
            data = np.frombuffer(data, dtype=np.uint8)
            data = data.reshape(240, 320)
            img = Image.fromarray(data)
            img.save('./test/test-{}.png'.format(count))
            count += 1
            data = b''
            start = False
        #     data = b''
    # client.close()
    # break


        # print(" ".join(hex(ord(n)) for n in content))
        # if prev_time == 0:
        #     prev_time = time.time_ns()
        #     continue
        # counter += 1
        # total_size += len(content)
        # if counter == 100:
        #     cur_time = time.time_ns()
        #     print("Data Size:", total_size)
        #     print("Bandwidth: %.3f KBps" % (total_size / ((cur_time - prev_time) / 1000000.0),))
            
        #     prev_time = cur_time
        #     counter = 0
        #     total_size = 0
        # print(len(content))
    