# a simple client socket
import socket
import numpy as np
from pickle import dumps, loads
import numpy as np

# arr = np.random.randint(low=-127, high=128, size=(28, 28), dtype=np.int8)
# print('client', arr)

# define socket address
TCP_IP = '127.0.0.1'  # ip of the server we want to connect to
TCP_PORT = 5000  # port used for communicating with the server
BUFFER_SIZE = 1024  # buffer size used when receiving data

# create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to server

def recvall(sock):
    BUFFER_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFFER_SIZE)
        data += part
        if len(part) < BUFFER_SIZE:
            break
    return data


# send message to the server
#message = b"I've been sent from the client!"
# message = dumps(arr)
s.connect((TCP_IP, TCP_PORT))
while True:
    include_img = True
    num_channels = 0
    message = dumps([include_img, num_channels])
    s.send(message) 
    print('client sent message:', message)
    data = recvall(s)
    img = np.frombuffer(data, dtype=np.uint8, count=-1, offset=0)
    img = img.reshape(224,224)
    print(img.shape, img.max(), img.min())
