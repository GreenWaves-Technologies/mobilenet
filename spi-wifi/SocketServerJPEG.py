from asyncio import constants
import socket
import time 
import numpy as np
from PIL import Image
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 8585))
s.listen(5)                 
 
prev_time = 0
cur_time = 0
counter = 0
total_size = 0
data = b''
start = False
totalPacket = 0
while True:
    client, addr = s.accept()
    print("Connected:", addr)
    while True:
        content = client.recv(730)
        if len(content) == 0:
            continue
        
        if int(content[1]) != 0 and not start:
            continue
        elif int(content[1]) == 0 and not start:
            start = True
        
        packetData = content[4:]
        real_length = int(content[2]) << 8 | int(content[3])
        total_size += real_length
        # print("Index:{}".format(int(content[1])))
        # print("Packet Length:{}/{}".format(real_length, total_size))
        if int(content[1]) == 0:
            totalPacket = packetData[0]
            print("Total Packet: {}".format(totalPacket))
            data = data + packetData[1:real_length]
        else:
            data = data + packetData[0:real_length]
        # for b in content:
        #     print(b, end = " ", flush=True)
        
        # if fullPacket:
        if int(content[1]) == totalPacket - 1:
            if prev_time == 0:
                prev_time = time.time_ns()
            else:
                cur_time = time.time_ns()
                print("Bw: %.3f KBps (%d Byte/%.1f ms)" % (total_size / ((cur_time - prev_time) / 1000 / 1000), total_size, (cur_time - prev_time) / 1000 / 1000))
                prev_time = cur_time
            total_size = 0
            # data = np.frombuffer(data, dtype=np.uint8)
            # data = data.reshape(240, 320)
            # img = Image.fromarray(data)
            # img.save('test.png')
            with open('test.jpg', 'wb') as f:
                f.write(data)
            data = b''
            totalPacket = 0
        
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
    