ID=0
NE16=1
START_MODEL=0
STOP_MODEL=33
SEC_FLASH=1
LOG_DIR="log_meas"

SUFF="_sq8"
if [ ${NE16} -eq 1 ]
then
	SUFF="_ne16"
fi

for ID in `seq $START_MODEL $STOP_MODEL`;
do
	touch main.c
	clean_and_run="make MODEL_ID=${ID} USE_PRIVILEGED_FLASH=${SEC_FLASH} MODEL_NE16=${NE16} clean_model model"
	echo ${clean_and_run}
	${clean_and_run} > ${LOG_DIR}/mobilenet_id_${ID}${SUFF}_at.log
done