import numpy as np
from PIL import Image
import time
import asyncio
import websockets
from threading import Thread
#from asyncio import Queue
import queue

async def image_notify(websocket, path, queue):
    
    while(True):        
        count = queue.get()
        await websocket.send("count %d"%count)



def image_generate(queue):

    count =0
    while(True):
        
        #Generate and save new images
        frame = np.random.randint(0,255,(224,224),dtype=np.uint8)
        im = Image.fromarray(frame)
        im.save("htdocs/imgs/frame.png")
        for i in range(8):
            h = np.random.randint(0,255,(32,32),dtype=np.uint8)
            im = Image.fromarray(frame)
            im.save("htdocs/imgs/h%d.png"%(i+1))
        
        #Let the websocket know that new images are ready
        if(queue.qsize()==0):
            queue.put_nowait(count)
            
        count=count+1
        print(count)
        
        time.sleep(0.25)

def start_websocket_loop(loop, server):
    loop.run_until_complete(server)
    loop.run_forever()


def main():
    
    #Start websocket server loop
    websocket_loop = asyncio.new_event_loop()
    
    #Queue to communicate between threads
    imgqueue = queue.Queue()
    
    #Start the websocket server
    start_server = websockets.serve(lambda ws,p : image_notify(ws,p,imgqueue), 'localhost', 8111, loop=websocket_loop)
    t1 = Thread(target=start_websocket_loop, args=(websocket_loop, start_server))
    t1.start()
    
    #Start image generator/saver
    t2 = Thread(target=image_generate, args=(imgqueue,))
    t2.start()
    
main()
    
    

