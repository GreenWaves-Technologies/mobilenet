#make clean all run platform=board MODEL_ID=15 FREQ_FC=250 FREQ_CL=175 HAVE_CAMERA=0 HAVE_LCD=0
#make clean all run platform=gvsoc MODEL_ID=0 FREQ_FC=250 FREQ_CL=175 HAVE_CAMERA=0 HAVE_LCD=0
#make clean all run platform=gvsoc MODEL_ID=0 FREQ_FC=250 FREQ_CL=175 HAVE_CAMERA=0 HAVE_LCD=0
source /root/gap_sdk/configs//gapuino_v2.sh 
make clean all run platform=board MODEL_ID=1 FREQ_FC=250 FREQ_CL=175 HAVE_CAMERA=1 HAVE_LCD=0 -C /root/gap_runner
