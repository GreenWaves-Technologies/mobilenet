#GUI imports
import matplotlib, sys
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pylab as plt
from scipy import ndimage
import tkinter as Tk
from mpl_toolkits.axes_grid1 import make_axes_locatable
# import im_tools
import time
import numpy as np
import socket
from pickle import dumps, loads
from multiprocessing import Process, Queue
from qclient import QClient

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
    def __init__(self, root, gap_client,
            TCP_IP='127.0.0.1', TCP_PORT=5000, 
            IMG_W=224, IMG_H=224, 
            HID_W=28, HID_H=28,
            MIN_HIDS=1, MAX_HIDS=32,
            HID_GRID=6, SKIP_HID=2
    ):
        self.root     = root
        self.gap_client = gap_client
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
        self.closing  = False;
        
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
        self.state_vars["Transmit Image"].set(0)
        self.chk_transmit = Tk.Checkbutton(master = self.bot_frame, text="Send Image", variable=self.state_vars["Transmit Image"])
        self.chk_transmit.pack(side=Tk.LEFT, expand=1, pady=5)

        #Create hidden unit slider
        self.state_vars["Num Hids"] = Tk.IntVar()
        self.state_vars["Num Hids"].set(1)
        
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

    #Define quit function
    def quit(self, *args):
        pass
                

    #Define refresh function
    #This is the main event loop for displaying updates in the GUI
    def do_refresh(self):
        include_img = self.state_vars['Transmit Image'].get() == 1
        
        #map slider value to the nearest power of 2
        #only a width of 2, 4, and 8 are supported
        # mapping = {2:2, 3:2, 4:4, 5:4, 6:8, 7:8, 8:8}
        # num_channels = mapping[self.state_vars['Num Hids'].get()]
        num_channels = self.state_vars['Num Hids'].get()
        self.state_vars['Num Hids'].set(num_channels)
        # control_config['num_channels'] = num_channels
        # control_config['quit'] = False
        
        img_bytes = self.IMG_W * self.IMG_H if include_img else 0
        hid_bytes = self.SPATIAL_DIM * num_channels
        num_bytes = self.time_bytes + hid_bytes
        num_bytes += img_bytes

        #If we're in the process of closing, don't run refresh
        if self.closing:
            return
        
        message = dumps([include_img, num_channels])
        self.gap_client.put((message, num_bytes))
        buff = self.gap_client.get()

        img = np.frombuffer(buff[0:img_bytes], dtype=np.uint8, count=-1, offset=0)
        hid = np.frombuffer(buff[img_bytes:img_bytes+hid_bytes], dtype=np.int8, count=-1, offset=0)
        time_vals = np.frombuffer(buff[img_bytes+hid_bytes:], dtype=np.uint32) * 10**-6
        hid = hid.reshape(num_channels, self.HID_H, self.HID_W)
        print(time_vals)


        # val = self.Qin.get()

        #Update image
        if include_img:
            img = img.reshape(self.IMG_H, self.IMG_W)
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
            
        self.root.after(100, self.do_refresh)

if __name__ == '__main__':
    TCP_IP = '192.168.0.105'
    TCP_PORT = 5000
    BUFFER_SIZE = 1024
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))
    
    # gap_Qin = Queue()
    # gap_Qout = Queue()
    gap_client = QClient(sock)
    gap_process = Process(target=gap_client.run, args=())
    
    root = Tk.Tk()
    #gui = GUI(root, sock, gap_Qin, gap_Qout)
    gui = GUI(root, gap_client)
    
    gap_process.start()
    root.after(200, gui.do_refresh) 
    root.mainloop()
