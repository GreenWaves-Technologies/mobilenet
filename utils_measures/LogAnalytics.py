import os
import string
import matplotlib.pyplot as plt
import csv
import sys
import numpy as np
import pickle


csv.field_size_limit(20000000)



# configs : FREQ_CL, FRE_FC, L2_SIZE, L1_SIZE
conflist = [[12,175000000,250000000,200000,48804],\
            [12,175000000,250000000,225000,48804],\
            [12,175000000,250000000,250000,48804],\
            [12,175000000,250000000,300000,48804],\
            [12,175000000,250000000,325000,48804],\
            [12,175000000,250000000,350000,48804]]
nconfig = len(conflist)
MODEL_LIST = {
    0 :"MobV1-224-1",
    1 :"MobV1-192-1",
    2 :"MobV1-160-1",
    3 :"MobV1-128-1",
    4 :"MobV1-224-075",
    5 :"MobV1-192-075",
    6 :"MobV1-160-075",
    7 :"MobV1-128-075",
    8 :"MobV1-224-05",
    9 :"MobV1-192-05",
    10:"MobV1-160-05",
    11:"MobV1-128-05",
    12:"MobV1-224-025",
    13:"MobV1-192-025",
    14:"MobV1-160-025",
    15:"MobV1-128-025",
    16:"MobV2-224-14",
    17:"MobV2-224-1",
    18:"MobV2-192-1",
    19:"MobV2-160-1",
    20:"MobV2-128-1",
    21:"MobV2-96-1",
    22:"MobV2-224-075",
    23:"MobV2-192-075",
    24:"MobV2-160-075",
    25:"MobV2-128-075",
    26:"MobV2-96-075",
    27:"MobV2-224-05",
    28:"MobV2-192-05",
    29:"MobV2-160-05",
    30:"MobV2-128-05",
    31:"MobV2-96-05",
    32:"MobV3-Min"
    }


# Read Data_Board
# 0: MAC,
# 1: MAC_CYC,
# 2: CYC_CNT ,
# 3: np.average(cluster)
# 4: np.average(soc)
# 5: np.average(memory)
# 6: n_points
 

with open('database.data', 'rb') as filehandle:
    # read the data as binary data stream
    data_board = pickle.load(filehandle)




print('------ Data Analysis ---------')


############### Printing Max FPS ################
print("This is the Maximum FPS")
for n in MODEL_LIST.keys():
    txt = MODEL_LIST[n]+'\t'
    n_p = 0
    for i in range(len(conflist)):
        if n in data_board[i].keys():
            #print(data_board[i][n])
            # [MAC,MAC_CYC,CYC_CNT]
            fps = conflist[i][1]/data_board[i][n][2]
            #print(fps)
            txt += '{:.2f}\t'.format(fps)
            n_p += 1
        else:
            txt += '\t'
    if n_p:
        print(txt)

print("This is the Avg MAX/Cycle")
for n in MODEL_LIST.keys():
    txt = MODEL_LIST[n]+'\t'
    n_p = 0
    for i in range(len(conflist)):
        if n in data_board[i].keys():
            #print(data_board[i][n])
            # [MAC,MAC_CYC,CYC_CNT]
            maccyc = data_board[i][n][1]
            #print(fps)
            txt += '{:.2f}\t'.format(maccyc)
            n_p += 1
        else:
            txt += '\t'
    if n_p:
        print(txt)

print("This is the Avg power")
for n in MODEL_LIST.keys():
    txt = MODEL_LIST[n]+'\t'
    n_p = 0
    for i in range(len(conflist)):
        if n in data_board[i].keys():
            # 3: np.average(cluster)
            cluster = data_board[i][n][3]*1.2
            # 4: np.average(soc)
            soc = data_board[i][n][4]*1.2
            # 5: np.average(memory)
            memory = data_board[i][n][5]*1.8
            #print(fps)
            latency = data_board[i][n][2] / (175 * 1000*1000)
            energy = (cluster + soc) * latency
            energy2 = (cluster + soc + memory) * latency
            txt += '| {:.2f} ({:.2f}),({:.2f}),({:.2f})\t'.format(latency,cluster,soc,memory)
            n_p += 1
        else:
            txt += '\t'
    if n_p:
        print(txt)


# Print Everything
print("This is the Avg power")
for n in MODEL_LIST.keys():
    txt = MODEL_LIST[n]+'\t'
    n_p = 0
    for i in range(len(conflist)):
        if n in data_board[i].keys():
            # [MAC,MAC_CYC,CYC_CNT]
            latency = data_board[i][n][2] / conflist[i][1]
            fps = 1/latency
            maccyc = data_board[i][n][1]
            mac = data_board[i][n][0]


            # 3: np.average(cluster)
            cluster = data_board[i][n][3]*1.2
            # 4: np.average(soc)
            soc = data_board[i][n][4]*1.2
            # 5: np.average(memory)
            memory = data_board[i][n][5]*1.8
            #print(fps)
            latency = data_board[i][n][2] / conflist[i][1]
            energy = (cluster + soc) * latency
            energy2 = (cluster + soc + memory) * latency
            txt += '| {:f}, {:f}, {:f}, {:f}, {:f}, {:f}, {:f}, {:f}, {:f}, {:f},\t'\
            		.format(latency,fps,maccyc,mac,cluster,soc,memory,latency,energy,energy2)
            n_p += 1
        else:
            txt += '\t'
    if n_p:
        print(txt)




##### Last Check ######
# CLK_CYCLES == 

print("This is to check")
for n in MODEL_LIST.keys():
    txt = MODEL_LIST[n]+'\t'
    n_p = 0
    for i in range(len(conflist)):
        if n in data_board[i].keys():
            # 3: np.average(cluster)
            n_points = data_board[i][n][6] / (1000)
            # 4: np.average(soc)
            clock_cycles = data_board[i][n][2] / (175 * 1000)
            # 5: np.average(memory)
            diff_perc = (n_points - clock_cycles) / clock_cycles
            txt += '{:.2f}\t'.format(diff_perc)
            #txt += '| {:.2f} {:.2f} \t'.format(n_points,clock_cycles)
            n_p += 1
        else:
            txt += '\t'
    if n_p:
        print(txt)

