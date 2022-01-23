import serial
import time
import socket
import numpy as np
from pickle import dumps, loads
import subprocess

class GAPServer:
    def __init__(self, 
                 TCP_IP='0.0.0.0', TCP_PORT=5000,
                 BUFFER_SIZE=1024,
                 baudrate=int(3 * 10**6), 
                 device='/dev/ttyUSB1', 
                 read_timeout=3, 
                 IMG_W=224, IMG_H=224, 
                 HID_W=28, HID_H=28, MAX_HIDS=8
    ):
        subprocess.Popen(['bash', '/root/gap_runner/run_gap.sh'])
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.BUFFER_SIZE = BUFFER_SIZE
        self.baudrate = baudrate
        self.device = device
        self.read_timeout = read_timeout
        self.IMG_W = IMG_W
        self.IMG_H = IMG_H
        self.HID_W = HID_W
        self.HID_H = HID_H
        self.MAX_HIDS = MAX_HIDS
        self.SPATIAL_DIM = HID_H * HID_W
        self.img_bytes = self.IMG_W * self.IMG_H
        self.time_bytes = 3*4
        
        self.ser = serial.Serial(device,baudrate=self.baudrate, timeout=self.read_timeout)
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
               
        
        # self.control_config = {'include_img': False, 'num_channels': self.MAX_HIDS, 'quit': False}
        # time.sleep(0.1)

    def flush_loop(self):
        #Make sure all writing has stopped
        while self.ser.in_waiting > 0:
            print("PSR: Flushing...")
            self.ser.flushInput()
            time.sleep(0.01)
    
    def run(self):
        print("PSR: Starting Python Simple Joint Serial Reader")
        
        self.sock.listen()
        conn, addr = self.sock.accept()
        while True:
            
            message = conn.recv(self.BUFFER_SIZE)
            if not message:
                break

            control_config = loads(message) 
            include_img, num_channels = control_config
            print('got config:', control_config)
                        
            #Flush serial input incase of pending writes
            self.flush_loop()
            
            #Send the data read ready signal
            print("PSR: Sending data read ready signal to Gap8")        
            sig = int(include_img)
            send_bytes = sig.to_bytes(1, 'little')
            send_bytes += num_channels.to_bytes(1, 'little')
            self.ser.write(send_bytes)
        
            #Determine number of bytes to read
            hid_bytes = self.SPATIAL_DIM * num_channels
            num_bytes = self.time_bytes + hid_bytes
            if include_img:
                num_bytes += self.img_bytes

            #read bytes from serial
            buff = self.ser.read(num_bytes)
            print("PSR: Read data from Gap8")        
            
            if len(buff) != num_bytes: 
                print("PSR: Got %d bytes expected %d bytes" % (len(buff), num_bytes))
                continue
            
            #forward bytes to client
            conn.send(buff) 
            print("PSR: Sent data back to client")        
            
            # img = None 
            # if include_img:
                # img = np.frombuffer(buff[0:img_bytes], dtype=np.uint8, count=-1, offset=0)
                # img = img.reshape(self.IMG_H, self.IMG_W)
                # hid = np.frombuffer(buff[img_bytes:img_bytes+hid_bytes], dtype=np.int8, count=-1, offset=0)
                # time_vals = np.frombuff(buff[img_bytes+hid_bytes:], dtype=np.uint32)
            # else:
                # hid = np.frombuffer(buff[:hid_bytes], dtype=np.int8, count=-1, offset=0)
                # time_vals = np.frombuff(buff[hid_bytes:], dtype=np.uint32)
            # hid = hid.reshape(num_channels, self.HID_H, self.HID_W)
            
            # serv_message = dumps([img, hid, time_vals])
            # conn.send(serv_message)
        
        # self.sock.close()

if __name__ == '__main__':
    server = GAPServer()
    while True:
        server.run()
