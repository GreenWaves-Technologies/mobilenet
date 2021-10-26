for NE16 in 0 1
do
	for ID in {0..34}
	do
		echo "Running model $ID in $NE16 ne16 mode and 1 fp16 mode --> log_model_id_${ID}_ne16_${NE16}_fp16_0.txt"
		make clean model MODEL_ID=$ID MODEL_NE16=$NE16 MODEL_FP16=0
		make all -j 8 platform=gvsoc MODEL_ID=$ID MODEL_NE16=$NE16 MODEL_FP16=0
		make run -j 8 platform=gvsoc MODEL_ID=$ID MODEL_NE16=$NE16 MODEL_FP16=0 > logs/log_model_id_${ID}_ne16_${NE16}_fp16_0.txt
		make nntool_predict
		cat nntool_prediction.txt >> logs/log_model_id_${ID}_ne16_${NE16}_fp16_0.txt
	done
done

# FP16
for ID in {0..34}
do
	echo "Running model $ID in $NE16 ne16 mode and 1 fp16 mode --> log_model_id_${ID}_ne16_${NE16}_fp16_1.txt"
	make clean model MODEL_ID=$ID MODEL_NE16=$NE16 MODEL_FP16=1
	make all -j 8 platform=gvsoc MODEL_ID=$ID MODEL_NE16=$NE16 MODEL_FP16=1
	make run -j 8 platform=gvsoc MODEL_ID=$ID MODEL_NE16=$NE16 MODEL_FP16=1 > log_model_id_${ID}_ne16_${NE16}_fp16_1.txt
	make nntool_predict
	cat nntool_prediction.txt >> logs/log_model_id_${ID}_ne16_${NE16}_fp16_0.txt
done

