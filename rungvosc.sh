#MODEL_ID=0 make run platform=gvsoc > output.txt

START_MODEL=17
STOP_MODEL=32
mkdir -p logs38/

##########################################
MODEL_L2_MEMORY=300000
MODEL_L1_MEMORY=46736
#12 Volt

for MODEL_L2_MEMORY in 325000 275000 250000 ; do # 350000 300000; do 
	
	FREQ_FC=250
	FREQ_CL=175
	for i in `seq $START_MODEL $STOP_MODEL`;
	do
		# run the autotiler
		MODEL_ID=$i FREQ_CL=$FREQ_CL FREQ_FC=$FREQ_FC MODEL_L2_MEMORY=$MODEL_L2_MEMORY make clean model  > logs38/atmodel\_$i\_$FREQ_CL\_$FREQ_FC\_$MODEL_L2_MEMORY\_$MODEL_L1_MEMORY.txt
		# check if the autotiler found a solution
		python3 utils_measures/parse_at_file.py logs38/atmodel\_$i\_$FREQ_CL\_$FREQ_FC\_$MODEL_L2_MEMORY\_$MODEL_L1_MEMORY.txt
		if [ $? -eq "1" ]; then
#			rm logs38/atmodel\_$i\_$FREQ_CL\_$FREQ_FC\_$MODEL_L2_MEMORY\_$MODEL_L1_MEMORY.txt
			continue
		fi
		
		# compile and run on board
		MODEL_ID=$i FREQ_CL=$FREQ_CL FREQ_FC=$FREQ_FC MODEL_L2_MEMORY=$MODEL_L2_MEMORY make all 
		python3 utils_measures/ps4444Measure.py logs38/power\_$i\_$FREQ_CL\_$FREQ_FC\_$MODEL_L2_MEMORY\_$MODEL_L1_MEMORY & 
		MODEL_ID=$i FREQ_CL=$FREQ_CL FREQ_FC=$FREQ_FC MODEL_L2_MEMORY=$MODEL_L2_MEMORY make run > logs38/output\_board\_log\_$i\_$FREQ_CL\_$FREQ_FC\_$MODEL_L2_MEMORY\_$MODEL_L1_MEMORY.txt
		
		# check if any error in the grph constructor
		python3 utils_measures/parse_out_file.py logs38/output\_board\_log\_$i\_$FREQ_CL\_$FREQ_FC\_$MODEL_L2_MEMORY\_$MODEL_L1_MEMORY.txt
		if [ $? -eq "1" ]; then # kill the measurement job
			for job in `jobs -p`
			do
				echo $job
			    kill -9 $job 
			done
			continue
		else # wait measurment job
			for job in `jobs -p`
			do
				echo $job
			    wait $job 
			done			
		fi

		python3 utils_measures/editlog.py logs38/power\_$i\_$FREQ_CL\_$FREQ_FC\_$MODEL_L2_MEMORY\_$MODEL_L1_MEMORY.csv  logs38/atmodel\_$i\_$FREQ_CL\_$FREQ_FC\_$MODEL_L2_MEMORY\_$MODEL_L1_MEMORY.txt logs38/output\_board\_log\_$i\_$FREQ_CL\_$FREQ_FC\_$MODEL_L2_MEMORY\_$MODEL_L1_MEMORY.txt logs38/log\_$i\_$FREQ_CL\_$FREQ_FC\_$MODEL_L2_MEMORY\_$MODEL_L1_MEMORY.txt

		rm logs38/power\_$i\_$FREQ_CL\_$FREQ_FC\_$MODEL_L2_MEMORY\_$MODEL_L1_MEMORY.csv 
		rm logs38/atmodel\_$i\_$FREQ_CL\_$FREQ_FC\_$MODEL_L2_MEMORY\_$MODEL_L1_MEMORY.txt
		rm logs38/output\_board\_log\_$i\_$FREQ_CL\_$FREQ_FC\_$MODEL_L2_MEMORY\_$MODEL_L1_MEMORY.txt

	done 
done
