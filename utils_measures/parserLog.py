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

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_total_stats(filename):
    text = None
    f = open(filename, "r")
    line = f.readline()
    while line:
        if 'Total' in line:
            text = line
        line = f.readline()
    f.close()     
    return text

data_board = [{} for x in range(nconfig)]
data_gvsoc = [{} for x in range(nconfig)]

basepath = './'
for entry in os.listdir(basepath):
    if os.path.isfile(os.path.join(basepath, entry)) and 'output' in entry:
        filename = basepath+entry

        print('---------------------------------')

        if 'board' in entry:

            print('This is board stats')

            t = get_total_stats(filename)
            if t is None:
                continue
            print(t)

            s = entry.replace('output_board_log_','').replace('.txt','').split('_')
            MODEL_ID=int(s[0])
            VOLT=int(s[1])
            FREQ_CL=int(s[2])
            FRE_FC =int(s[3])
            L2_SIZE=int(s[4])
            L1_SIZE=int(s[5])
            print(VOLT,FREQ_CL,FRE_FC,L2_SIZE,L1_SIZE)

            # check which config it is
            found = False
            for c_ix, c in enumerate(conflist):
                if c == [VOLT,FREQ_CL,FRE_FC,L2_SIZE,L1_SIZE]:
                    found=True
                    break
            if (MODEL_ID==16):
                print('**************************\n**************************\n**************************\n**************************\n')
            if not found:
                print('Not recognized Log')
                pass
            
            s = t.replace(':','').replace(',','').replace('\n','').split(' ')
            x = [ item for item in s if is_number(item)]
            CYC_CNT = int(x[0])
            MAC=int(x[1])
            MAC_CYC=float(x[2])
            print(MODEL_ID,MAC_CYC)

            s = entry.replace('output_board_log_','power_').replace('.txt','.csv')    
            cluster = []
            soc = []
            memory = [] 
            with open(s, newline='') as f:
                reader = csv.reader(f,quoting=csv.QUOTE_NONNUMERIC)
                for r, row in enumerate(reader):
                    if r == 0:
                        print("Reading cluster data")
                        cluster = np.array(row)
                    elif r == 1:
                        print("Reading soc data")
                        soc = np.array(row)         
                    elif r == 2:
                        print("Reading memory data")
                        memory = np.array(row)  
                    else:
                        print("Reading extra lines")

            n_points = len(cluster)

            data_board[c_ix][MODEL_ID] = [MAC,MAC_CYC,CYC_CNT,np.average(cluster),np.average(soc),np.average(memory),n_points]

        else:

            print('Not recognized file')


with open('database.data', 'wb') as filehandle:
    # store the data as binary data stream
    pickle.dump(data_board, filehandle)

print('------ Data Analysis ---------')
#conflist = [
#     0       [175000000,250000000,200000,48804],
#     1       [50000000,250000000,200000,48804],\
#     2       [175000000,250000000,250000,48804],
#     3       [50000000,250000000,250000,48804],\
#     4       [175000000,250000000,300000,48804],
#     5       [50000000,250000000,300000,48804],\
#     6       [175000000,250000000,350000,48804],
#     7       [50000000,250000000,350000,48804],
#     8       [175000000,250000000,400000,48804],
#     9       [50000000,250000000,400000,48804]]

#print(data_board[8])

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

# 0: MAC
# 1: MAC_CYC
# 2: CYC_CNT
fig, (ax,ax2) = plt.subplots(1,2)


for i in range(len(conflist)):
    print(conflist[i])
    x = []
    y = []
    for item in sorted(data_board[i].keys()):
        x.append(data_board[i][item][0])
        y.append(data_board[i][item][3]+data_board[i][item][4]+data_board[i][item][5])
        #y.append(conflist[i][0]/data_board[i][item][2])
        #ax.scatter(data_board[i][item][0], data_board[i][item][1])
    ax.scatter(x,y,label='L2='+str(int(conflist[i][3]/1000))+'k')
    print("\n")

ax.set_xlabel('MAC')
ax.set_ylabel('MAC/Cyc')
ax.set_title('MAC/Cyc @ FC=250M, FREQ_CL=175M')
ax.set_ylim([1,9])
ax.legend()

plt.plot()

#exit(0)
#
## 0: MAC
## 1: MAC_CYC
## 2: CYC_CNT
#fig, (ax,ax2) = plt.subplots(1,2)
#
#
#for i in range(len(conflist)):
#    print(conflist[i])
#    x = []
#    y = []
#    for item in sorted(data_board[i].keys()):
#        print(item)
#        x.append(data_board[i][item][0])
#        y.append(data_board[i][item][1])
#        #y.append(conflist[i][0]/data_board[i][item][2])
#        #ax.scatter(data_board[i][item][0], data_board[i][item][1])
#    ax.scatter(x,y,label='L2='+str(int(conflist[i][2]/1000))+'k')
#    print("\n")
#
#ax.set_xlabel('MAC')
#ax.set_ylabel('MAC/Cyc')
#ax.set_title('MAC/Cyc @ FC=250M, FREQ_CL=175M')
#ax.set_ylim([1,9])
#ax.legend()


