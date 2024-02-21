

PLATFORM=gvsoc

START_MODEL=19
STOP_MODEL=32

LOG_DIR="../log_meas"
if [[ ! -e $LOG_DIR ]]; then
    mkdir $LOG_DIR
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

MEAS_SCRIPT=$GAP_SDK_HOME/utils/power_meas_utils/ps4444Measure.py
if [ "$PLATFORM" = "gvsoc" ]; then 
    echo "Running on Gvsoc"
    OPTS_PLATFORM="-DCONFIG_PLATFORM_GVSOC=y"
    MEAS_CMD="echo \"Gvsoc does not have power\" >"
    WAIT_MEAS=
else
    echo "Running on BOARD"
    OPTS_PLATFORM="-DCONFIG_PLATFORM_BOARD=y -DCONFIG_GPIO_MEAS=y"
    MEAS_CMD=python ${MEAS_SCRIPT}
    WAIT_MEAS=wait_finished_job
fi;

meas_cmd () {
    ${MEAS_CMD} $1
}
wait_meas_cmd () {
    ${WAIT_MEAS}
}

OPTS_370MHZ="-DCONFIG_VOLTAGE=800 -DCONFIG_FREQUENCY_PERIPH=370000000 -DCONFIG_FREQUENCY_FC=370000000 -DCONFIG_FREQUENCY_CLUSTER=370000000"
OPTS_240MHZ="-DCONFIG_VOLTAGE=650 -DCONFIG_FREQUENCY_PERIPH=240000000 -DCONFIG_FREQUENCY_FC=240000000 -DCONFIG_FREQUENCY_CLUSTER=240000000"

for ID in `seq $START_MODEL $STOP_MODEL`;
do
    # common options
    CMAKE_CMD="cmake ../ -DCONFIG_MODEL_ID=${ID} ${OPTS_PLATFORM}"

	${CMAKE_CMD} ${OPTS_370MHZ}
	make clean_model model > ${LOG_DIR}/mobilenet_id_${ID}_${SUFF}_at.log

	# High Performance
    meas_cmd ${LOG_DIR}/mobilenet_id_${ID}_${SUFF}_370MHz_800mV
	make run -j > ${LOG_DIR}/mobilenet_id_${ID}_${SUFF}_perf_370MHz.log
    wait_meas_cmd

	# Energy Efficient
	${CMAKE_CMD} ${OPTS_240MHZ}
    meas_cmd ${LOG_DIR}/mobilenet_id_${ID}_${SUFF}_240MHz_650mV
	make run -j > ${LOG_DIR}/mobilenet_id_${ID}_${SUFF}_perf_240MHz.log
    wait_meas_cmd
done
