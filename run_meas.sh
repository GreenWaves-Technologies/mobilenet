if [ -z $GAP_SDK_HOME ]; then
	echo "Source the sdk before"
	exit 1
fi

START_MODEL=33
STOP_MODEL=33
LOGDIR=logs
mkdir -p $LOGDIR/
##########################################
FP16=0
HWC=0
MODES=('CHW' 'NE16' 'HWC') # 'FP16_CHW' 'FP16_HWC')

export RAM_TYPE="OSPI"
export FLASH_TYPE="OSPI"
export AT_LOG_LEVEL=2
export PMSIS_OS=pulpos

for MODEL_ID in `seq $START_MODEL $STOP_MODEL`;
do
	for MODE in "${MODES[@]}"
	do
		case $MODE in
			CHW)
				export MODEL_NE16=0
				export MODEL_FP16=0
				export MODEL_HWC=0
				;;
			NE16)
				export MODEL_NE16=1
				export MODEL_FP16=0
				export MODEL_HWC=0
				;;
			HWC)
				export MODEL_NE16=0
				export MODEL_FP16=0
				export MODEL_HWC=1
				;;
			FP16_CHW)
				export MODEL_NE16=0
				export MODEL_FP16=1
				export MODEL_HWC=0
				;;
			FP16_HWC)
				export MODEL_NE16=0
				export MODEL_FP16=1
				export MODEL_HWC=1
				;;
			*)
				echo "Mode $MODE not supported"
				exit 1
		esac
		MODEL_EXT="${MODEL_ID}"
		if [ ${MODEL_NE16} -gt 0 ]; then
			MODEL_EXT="${MODEL_EXT}_NE16"
		else
			if [ ${MODEL_FP16} -gt 0 ]; then
				MODEL_EXT="${MODEL_EXT}_FP16"
			fi
			if [ ${MODEL_HWC} -gt 0 ]; then
				MODEL_EXT="${MODEL_EXT}_HWC"
			fi
		fi
		echo "Running mode $MODE: MODEL_ID=$MODEL_ID MODEL_NE16=$MODEL_NE16 MODEL_FP16=$MODEL_FP16 MODEL_HWC=$MODEL_HWC RAM_TYPE=$RAM_TYPE FLASH_TYPE=$FLASH_TYPE AT_LOG_LEVEL=$AT_LOG_LEVEL"
		make clean clean_model model MODEL_ID=$MODEL_ID MODEL_NE16=$MODEL_NE16 MODEL_FP16=$MODEL_FP16 MODEL_HWC=$MODEL_HWC RAM_TYPE=$RAM_TYPE FLASH_TYPE=$FLASH_TYPE AT_LOG_LEVEL=$AT_LOG_LEVEL \
				> $LOGDIR/atmodel\_${MODEL_EXT}.txt
		# check if the autotiler found a solution
		python3 utils_measures/parse_at_file.py $LOGDIR/atmodel\_${MODEL_EXT}.txt
		if [ $? -eq "1" ]; then
			echo "Something went wrong with the model generation"
			continue
		fi

		# compile and flash
		make all -j MODEL_ID=$MODEL_ID MODEL_NE16=$MODEL_NE16 MODEL_FP16=$MODEL_FP16 MODEL_HWC=$MODEL_HWC RAM_TYPE=$RAM_TYPE FLASH_TYPE=$FLASH_TYPE AT_LOG_LEVEL=$AT_LOG_LEVEL

		for LOW_POWER_MODE in 0 1 ;
		do
			if [ $LOW_POWER_MODE -gt 0 ]; then
				FREQ=240
				export VOLTAGE=650
			else
				FREQ=370
				export VOLTAGE=800
			fi
			export FREQ_CL=$FREQ
			export FREQ_FC=$FREQ
			export FREQ_PE=$FREQ
			DVFS_FLAGS="FREQ_FC=$FREQ_FC FREQ_CL=$FREQ_CL FREQ_PE=$FREQ_PE VOLTAGE=$VOLTAGE"

			LOG_EXT="${MODEL_EXT}_${FREQ}_${VOLTAGE}"

			# generate the model
			echo "$LOG_EXT"
			touch BUILD_MODEL_SQ8BIT/*
			touch BUILD_MODEL_NE16/*
			touch BUILD_MODEL_FP16/*
			touch main.c
			touch main_fp16.c

			# compile and run on board
			make build -j MODEL_ID=$MODEL_ID MODEL_NE16=$MODEL_NE16 MODEL_FP16=$MODEL_FP16 MODEL_HWC=$MODEL_HWC RAM_TYPE=$RAM_TYPE FLASH_TYPE=$FLASH_TYPE AT_LOG_LEVEL=$AT_LOG_LEVEL
			python3 utils_measures/ps4444Measure.py $LOGDIR/power\_${LOG_EXT} & 
			make run MODEL_ID=$MODEL_ID MODEL_NE16=$MODEL_NE16 MODEL_FP16=$MODEL_FP16 MODEL_HWC=$MODEL_HWC RAM_TYPE=$RAM_TYPE FLASH_TYPE=$FLASH_TYPE AT_LOG_LEVEL=$AT_LOG_LEVEL \
					> $LOGDIR/output\_board\_log\_${LOG_EXT}.txt

			# check if any error in the grph constructor
			python3 utils_measures/parse_out_file.py $LOGDIR/output\_board\_log\_${LOG_EXT}.txt
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

			python3 utils_measures/editlog.py $LOGDIR/power\_${LOG_EXT}.csv $LOGDIR/atmodel\_${MODEL_EXT}.txt $LOGDIR/output\_board\_log\_${LOG_EXT}.txt $LOGDIR/log\_${LOG_EXT}

			rm $LOGDIR/power\_${LOG_EXT}.csv
			rm $LOGDIR/output\_board\_log\_${LOG_EXT}.txt
		done
		rm $LOGDIR/atmodel\_${MODEL_EXT}.txt
	done
done
