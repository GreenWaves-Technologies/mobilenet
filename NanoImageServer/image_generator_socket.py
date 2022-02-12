import numpy as np
from PIL import Image
import time
import shutil
import asyncio
import websockets

async def image_server(websocket, path):
    #name = await websocket.recv()
    #print(name)

    count=0;
    while(True):
        frame = np.random.randint(0,255,(224,224),dtype=np.uint8)
        im = Image.fromarray(frame)
        im.save("htdocs/imgs/frame.png")
        
        for i in range(8):
            h = np.random.randint(0,255,(32,32),dtype=np.uint8)
            im = Image.fromarray(frame)
            im.save("htdocs/imgs/h%d.png"%(i+1))
        
        await websocket.send("count %d"%count)
        time.sleep(0.25)
        count=count+1
        print(count)


start_server = websockets.serve(image_server, 'localhost', 8111)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
