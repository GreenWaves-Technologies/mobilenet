import socket
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
    message = b'0 32\r'
    sock.sendall(message)
    print('sent message % s' % message)
    buff = recvall(sock, 8*28*28, 28*28)
    print(len(buff))
sock.close()

