#this script will be executed inside the container
#only way I could figure to get source to work
#it is called inside run.sh

source /root/gap_sdk/configs/gapuino_v2.sh
make clean all run platform=board -C /root/gap_runner/gap
