import socket
import time
# from multiprocessing import Queue, Process
# import numpy as np
def recvall(sock, target_size=4096, buffer_size=4096):
    data = b''
    while True:
        part = sock.recv(buffer_size)
        if not part:
            return None
        data += part
        if len(data) == target_size:
            break
    return data

server_ip = '192.168.0.216'
server_port = 80

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_ip,  server_port))
while True:
    start = time.time()
    message = b'0 32\r'
    sock.sendall(message)
    buff = recvall(sock, 224*224, 1024)
    print(len(buff), time.time() - start)
sock.close()
