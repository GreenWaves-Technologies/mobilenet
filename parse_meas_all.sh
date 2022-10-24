
for ID in `seq 0 33`;
do
#	python $GAP_SDK_HOME/utils/power_meas_utils/log_to_csv.py --model_name mobilenet_id_${ID} --suffix ne16 --freq 370 --voltage 800 --log_dir log_meas/ --out_file meas_all.csv
#	python $GAP_SDK_HOME/utils/power_meas_utils/log_to_csv.py --model_name mobilenet_id_${ID} --suffix ne16 --freq 240 --voltage 650 --log_dir log_meas/ --out_file meas_all.csv
	python $GAP_SDK_HOME/utils/power_meas_utils/log_to_csv.py --model_name mobilenet_id_${ID} --suffix fp16 --freq 370 --voltage 800 --log_dir log_meas/ --out_file meas_all.csv
	python $GAP_SDK_HOME/utils/power_meas_utils/log_to_csv.py --model_name mobilenet_id_${ID} --suffix fp16 --freq 240 --voltage 650 --log_dir log_meas/ --out_file meas_all.csv
done