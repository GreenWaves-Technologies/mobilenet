#!/usr/bin/python
import sys
import matplotlib.pyplot as plt
import os
import pandas as pd
import re

CLASS_MATCH = re.compile(r'Predicted class:\t(?P<class>[0-9]+)\n')
PERF_MATCH = re.compile(r'\t\t\t Total: Cycles:   (?P<cycles>[0-9]+), Operations:  (?P<operations>[0-9]+), Operations\/Cycle: (?P<opovercyc>[0-9.]+)\n')
NUM_MODELS = 33
GT_predictions = {0: 42, 1: 77, 2: 42, 3: 67, 4: 42, 5: 121, 6: 311, 7: 77, 8: 78, 9: 69, 10: 42, 11: 311, 12: 77, 13: 39, 14: 121, 15: 121, 16: 49, 17: 42, 18: 42, 19: 43, 20: 42, 21: 42, 22: 42, 23: 42, 24: 42, 25: 42, 26: 77, 27: 42, 28: 42, 29: 42, 30: 39, 31: 276, 32: 42}
# predicted values with emul mode (tested to be ok in validation) on ILSVRC2012_val_00011158 image
GT_performance = {0: 6.75633, 1: 6.958425, 2: 7.767089, 3: 7.671721, 4: 7.456866, 5: 7.5372, 6: 7.676829, 7: 7.449675, 8: 7.125032, 9: 7.084658, 10: 7.278495, 11: 6.427716, 12: 6.063097, 13: 5.876167, 14: 5.601814, 15: 5.282983, 16: 4.527786, 17: 5.913087, 18: 5.981472, 19: 5.727079, 20: 5.791325, 21: 5.313634, 22: 5.585749, 23: 5.406378, 24: 5.62603, 25: 5.200447, 26: 4.97893, 27: 4.864435, 28: 4.80691, 29: 4.626174, 30: 4.272549, 31: 3.602734, 32: 5.016086}
# MAC/Cyc Performance evaluated with gap8 v3 with: FC_FREQ: 250MHz CL_FREQ: 175MHz

try:
	TARGET_PLATFORM = os.environ['PLPTEST_PLATFORM']
except:
	TARGET_PLATFORM = 'gvsoc'

def main():
	print("Target Platform: ", TARGET_PLATFORM)
	starting_model_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
	final_model_id = int(sys.argv[2]) if len(sys.argv) > 2 else NUM_MODELS
	
	out_predictions = {}
	for model_id in range(starting_model_id, final_model_id):
		shell_command = 'make clean all run platform={} MODEL_ID={}'.format(TARGET_PLATFORM, model_id)
		print(shell_command)
		stream = os.popen(shell_command)
		platform_log = stream.readlines()
		platform_prediction = None
		platform_performance = (None, None)
		for line in platform_log:
			m = CLASS_MATCH.search(line)
			m_perf = PERF_MATCH.search(line)
			if m_perf:
				platform_performance = (int(m_perf['cycles']), float(m_perf['opovercyc']))
			if m:
				platform_prediction = int(m['class'])

		stream_tflite = os.popen('make test_tflite MODEL_ID={}'.format(model_id))
		tflite_log = stream_tflite.readlines()
		tflite_prediction = None
		for line in tflite_log:
			m = CLASS_MATCH.search(line)
			if m:
				tflite_prediction = int(m['class'])
				break

		TEST = "OK" if platform_prediction == GT_predictions[model_id] else "FAIL"
		PERF_CHECK = "BETTER" if platform_performance[1] is not None and \
								 platform_performance[1] > GT_performance[model_id] else "WORSE"

		out_predictions.update({model_id: [platform_prediction, GT_predictions[model_id], tflite_prediction, platform_performance[0], platform_performance[1], PERF_CHECK, TEST]})
		print(out_predictions)

	df = pd.DataFrame.from_dict(out_predictions, orient='index', columns=['platform', 'ground truth', 'tflite', 'Cycles', 'Mac/Cyc', 'Perf check', 'passed'])
	pd.set_option('display.max_columns', 8)
	print(df)
	failed_models = [k for k, v in out_predictions.items() if v[-1] == "FAIL"]
	if len(failed_models) > 0:
		print("Failing models: ", failed_models)
		return 1
	return 0


if __name__ == "__main__":
	main()
