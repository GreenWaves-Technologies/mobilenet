#GUI imports
import matplotlib, sys
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pylab as plt
from scipy import ndimage
import tkinter as Tk
from mpl_toolkits.axes_grid1 import make_axes_locatable
import time
import numpy as np
import socket
from pickle import dumps, loads
from multiprocessing import Process, Queue
from utils.network import QClient, buff2numpy
from utils.fix import Fixer
import cv2
import torch
import os
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

def gallery(array, ncols=3, nrows=3, pad=1, pad_value=0):
    array = np.pad(array,[[0,0],[1,1],[1,1]],'constant',constant_values=pad_value)
    nindex, height, width = array.shape
    n_extra = ncols*nrows - nindex
    array = np.concatenate((array,pad_value*np.ones((n_extra,height, width))))
    # want result.shape = (height*nrows, width*ncols, intensity)
    result = (array.reshape(nrows, ncols, height, width)
              .swapaxes(1,2)
              .reshape(height*nrows, width*ncols))
    return result


class GUI:
    def __init__(self, root,
            IMG_W=224, IMG_H=224, 
            HID_W=28, HID_H=28,
            MIN_HIDS=1, MAX_HIDS=32,
            HID_GRID=6, SKIP_HID=2,
            num_dets=50
    ):
        self.root     = root
        self.MAX_HIDS = MAX_HIDS
        self.MIN_HIDS = MIN_HIDS
        self.SKIP_HID = SKIP_HID
        self.HID_W    = HID_W
        self.HID_H    = HID_H
        self.HID_GRID = HID_GRID
        self.IMG_W    = IMG_W
        self.IMG_H    = IMG_H 
        self.state_vars={}
        self.frame_rate_timer=time.time()
        self.closing  = False
        self.num_dets = num_dets
        dummy_dets = np.zeros((self.num_dets, 6), dtype=np.uint16)
        self.num_dets_bytes = len(dumps(dummy_dets))
        self.path = os.path.join(os.environ['HOME'], 'record/')
        
        self.SPATIAL_DIM = HID_H * HID_W
        self.time_bytes = 3*4
       
        self.stats={}
        self.stats["cloud_frame_rate"] = []
        self.time_stat_keys=[ "gap8_sensing", "gap8_comm","gap8_compute", "cloud_compute"]
        self.time_stat_names=[ "gs", "gt","gc", "cc"]
        for key in self.time_stat_keys:
            self.stats[key]=[]        
                

        #Set winodow properties
        self.root.wm_title("Distributed Prediction GUI")
        self.root.configure(bg='white')

        #Define top Frame
        self.top_frame = Tk.Frame(self.root)
        self.top_frame.configure(bg='white')
        self.top_frame.pack(side="top", fill=Tk.BOTH, expand=1)

        #Define middle Frame
        self.mid_frame = Tk.Frame(self.root)
        self.mid_frame.configure(bg='white')
        self.mid_frame.pack(side="top",fill=Tk.BOTH, expand=1)

        #Define bottom  Frame
        self.bot_frame = Tk.Frame(root)
        self.bot_frame.pack(side="top", fill=Tk.BOTH, expand=0)
        self.bot_frame.config(relief=Tk.GROOVE, bd=2)

        #Create canvas to display Image
        tmp_img        = np.ones((self.IMG_H,self.IMG_W))
        fig_image      = plt.figure(figsize=(4,4))
        ax             = plt.gca()
        plt.title("Remote Image")
        self.im_image  = ax.imshow(tmp_img,cmap="gray") 
        plt.tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, right=False, left=False, labelleft=False)
        divider        = make_axes_locatable(ax)
        cax            = divider.append_axes("right", size="5%", pad=0.05)
        self.im_image.set_clim(0,255)
        plt.colorbar(self.im_image, cax=cax)

        #Embed the Image
        self.canvas_image = FigureCanvasTkAgg(fig_image, master=self.top_frame)
        self.canvas_image.draw()
        self.canvas_image.get_tk_widget().pack(side=Tk.LEFT, pady=5, padx=5, fill=Tk.BOTH, expand=1)

        #Create canvas to Diaply Hids
        tmp_hids = gallery(np.zeros((8,self.HID_W,self.HID_H)), ncols=self.HID_GRID, nrows=self.HID_GRID)
        fig_hids = plt.figure(figsize=(4,4))
        ax             = plt.gca()
        self.im_hids        = ax.imshow(tmp_hids,cmap="jet") 
        plt.tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, right=False, left=False, labelleft=False)
        plt.title("Remote Hidden Activations")
        divider        = make_axes_locatable(ax)
        cax            = divider.append_axes("right", size="5%", pad=0.05)
        self.im_hids.set_clim(0,6)
        plt.colorbar(self.im_hids, cax=cax)

        #Embed the Hids
        self.canvas_hids = FigureCanvasTkAgg(fig_hids, master=self.top_frame)
        self.canvas_hids.draw()
        self.canvas_hids.get_tk_widget().pack(side=Tk.LEFT, pady=5, padx=5, fill=Tk.BOTH, expand=1)

        #Create canvas to display framerate
        fig_fr = plt.figure(figsize=(4,2))
        self.ax_fr    = plt.gca()
        self.line_fr, = self.ax_fr.plot([], [], color='b')
        self.ax_fr.axis([0, 10, 0, 1])
        plt.title("Frame Rate")
        plt.ylabel("FPS")
        plt.grid(True);
        self.canvas_fr = FigureCanvasTkAgg(fig_fr, master=self.mid_frame)
        self.canvas_fr.draw()
        self.canvas_fr.get_tk_widget().pack(side=Tk.LEFT, pady=5, padx=5, fill=Tk.BOTH, expand=1)


        #Create canvas to display timing stats
        fig_time = plt.figure(figsize=(4,2))
        self.ax_time    = plt.gca()
        self.ax_fr.axis([0, 10, 0, 1])
        plt.title("Process Times")
        self.canvas_time = FigureCanvasTkAgg(fig_time, master=self.mid_frame)
        self.canvas_time.draw()
        self.canvas_time.get_tk_widget().pack(side=Tk.LEFT, pady=5, padx=5, fill=Tk.BOTH, expand=1)        

        #Create control check box
        self.state_vars["Transmit Image"] = Tk.IntVar()
        self.state_vars["Transmit Image"].set(1)
        self.chk_transmit = Tk.Checkbutton(master = self.bot_frame, text="Send Image", variable=self.state_vars["Transmit Image"])
        self.chk_transmit.pack(side=Tk.LEFT, expand=1, pady=5)

        #Create hidden unit slider
        self.state_vars["Num Hids"] = Tk.IntVar()
        self.state_vars["Num Hids"].set(32)
        
        self.hid_select = Tk.Scale(master=self.bot_frame, 
            label="Hidden Dimension", showvalue=False, length=300, 
            sliderlength=self.MAX_HIDS, tickinterval=self.SKIP_HID, 
            orient=Tk.HORIZONTAL, 
            from_=self.MIN_HIDS, to=self.MAX_HIDS, 
            variable=self.state_vars["Num Hids"]
        )
        self.hid_select.set(self.state_vars["Num Hids"].get())
        self.hid_select.pack(side=Tk.LEFT, expand=1, pady=5)
        # for val in [2,4,8]:
            # Tk.Radiobutton(master = self.bot_frame, 
                          # text="Use K=%d"%val,
                          # padx = 5, 
                          # variable=self.state_vars["Num Hids"], 
                          # value=val).pack(side=Tk.LEFT, expand=1, pady=5)
        
        #Create a quit button
        self.button_quit = Tk.Button(master = self.bot_frame, text = 'Quit', command = self.quit)
        self.button_quit.pack(side=Tk.LEFT,expand=1, pady=5)

        self.frame_count = 0

    #Define quit function
    def quit(self, *args):
        pass
                

    #Define refresh function
    #This is the main event loop for displaying updates in the GUI
    def do_refresh(self):
        fname = '%s/frame_%05.0f.pkl' % (self.path, self.frame_count)
        while not os.path.isfile(fname):
            time.sleep(0.01)

        with open(fname, 'rb') as f:
            data = pickle.load(f)
            # data = np.load(f, allow_pickle=True)

        img = data['img']
        hid = data['hid'][0]
        dets = data['dets']
        
                
        
        #Update image
        if img is not None:
            img = img.reshape(self.IMG_H, self.IMG_W, 1)
            print(img.mean(), img.std())
            img = np.concatenate([img]*3, axis=-1)
        
        # img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        for det in dets:
            box = det[0:4]
            score = det[4]
            if score < 10:
                continue
            label = CLASSES[det[5]]
            img = cv2.rectangle(img,
                (box[0], box[1]),
                (box[2], box[3]),
                (255,255,0),
                thickness=1
            )
            img = cv2.putText(img,
                '%s: %s' % (label, score),
                (box[0], box[1] - 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255,255,0),
                1
            )


        self.im_image.set_data(img)
        self.canvas_image.draw()  
    
        # Update hids
        hid_im = gallery(hid, ncols=self.HID_GRID, nrows=self.HID_GRID)
        self.im_hids.set_data(hid_im)
        self.canvas_hids.draw()
    
        #Updat times
        proc_time = time.time() - self.frame_rate_timer
        print('GUI: approx fps = ', 1/proc_time)
        self.frame_rate_timer = time.time() 
            
        #Update framerate graph
        # self.stats["cloud_frame_rate"].append(1/proc_time) 
        # frame_count = len(self.stats["cloud_frame_rate"])
        # if(frame_count>20):
            # x = np.arange(frame_count-20,frame_count)
            # y = self.stats["cloud_frame_rate"][-20:]
            # minx = x[0]
            # maxx = x[-1]
        # else:
            # x = np.arange(frame_count)
            # y = self.stats["cloud_frame_rate"]
            # minx = 0
            # maxx = 19
        # if(frame_count>1):
            # self.line_fr.set_data(x,y)
            # self.ax_fr.axis([minx, maxx, 0, 1.05*np.max(y)])
            # self.canvas_fr.draw()

        #Update times graph
        # ys=[]
        # for key in self.time_stat_keys:
            # self.stats[key].append(val["time"][key])
            
            # if(frame_count>20):
                # ys.append( self.stats[key][-20:] )
            # else:
                # ys.append( self.stats[key])
        
        # if(frame_count>1):
            # self.ax_time.cla()
            # self.ax_time.stackplot(x,ys)
            # self.ax_time.set_ylim(-1, 1.2*np.max(np.sum(ys,axis=0)))
            # plt.title("Process Times")
            # plt.ylabel('Time (s)')
            # plt.legend(self.time_stat_names,ncol=4,loc="lower center")
            # plt.grid(True);
            # self.canvas_time.draw()
        

        #print("GUI: Run times:",val["time"])
        
        print("GUI: gui has refresed")
        self.frame_count += 1
            
        self.root.after(100, self.do_refresh)

if __name__ == '__main__':
    root = Tk.Tk()
    gui = GUI(root)
    
    root.after(200, gui.do_refresh) 
    root.mainloop()
