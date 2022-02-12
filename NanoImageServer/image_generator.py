import numpy as np
from PIL import Image
import time
import shutil

def main():
    
    count=0;
    while(True):
        frame = np.random.randint(0,255,(224,224),dtype=np.uint8)
        im = Image.fromarray(frame)
        im.save("htdocs/imgs/frame.png")
        
        for i in range(8):
            h = np.random.randint(0,255,(32,32),dtype=np.uint8)
            im = Image.fromarray(frame)
            im.save("htdocs/imgs/h%d.png"%(i+1))
        
        time.sleep(0.25)
        count=count+1
        print(count)
        
main();