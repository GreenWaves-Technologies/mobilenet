ID=0
NE16=1
FP16=1

START_MODEL=20
STOP_MODEL=33
SEC_FLASH=1
LOG_DIR="log_meas"
if [[ ! -e $LOG_DIR ]]; then
    mkdir $LOG_DIR
fi

MAIN=main.c
SUFF="sq8"
if [ ${NE16} -eq 1 ]
then
	SUFF="ne16"
fi
if [ ${FP16} -eq 1 ]
then
	MAIN=main_fp16.c
	SUFF="fp16"
fi

wait_finished_job() {
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
}

for ID in `seq $START_MODEL $STOP_MODEL`;
do
	touch ${MAIN}
	make_cmd="make MODEL_ID=${ID} USE_PRIVILEGED_FLASH=${SEC_FLASH} MODEL_NE16=${NE16} MODEL_FP16=${FP16} MODEL_HWC=1"
	echo ${make_cmd}
	${make_cmd} model > ${LOG_DIR}/mobilenet_id_${ID}_${SUFF}_at.log
	${make_cmd} io=uart all -j

	# High Performance
	F=370
	V=800
	python $GAP_SDK_HOME/utils/power_meas_utils/ps4444Measure.py ${LOG_DIR}/mobilenet_id_${ID}_${SUFF}_${F}MHz_${V}mV & touch ${MAIN} && \
	${make_cmd} MEAS=1 FREQ_CL=${F} FREQ_FC=${F} FREQ_PE=${F} VOLTAGE=${V} io=uart run
	wait_finished_job

	# Energy Efficient
	F=240
	V=650
	python $GAP_SDK_HOME/utils/power_meas_utils/ps4444Measure.py ${LOG_DIR}/mobilenet_id_${ID}_${SUFF}_${F}MHz_${V}mV & touch ${MAIN} && \
	${make_cmd} MEAS=1 FREQ_CL=${F} FREQ_FC=${F} FREQ_PE=${F} VOLTAGE=${V} io=uart run
	wait_finished_job
done
