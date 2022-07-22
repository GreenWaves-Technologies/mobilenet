#!/usr/bin/env python3

import sys
import os
import pandas as pd
import re
import signal
from datetime import date

CLASS_MATCH = re.compile(r'Predicted class:\t(?P<class>[0-9]+)\n')
PERF_MATCH = re.compile(r'\s+Total:\s+Cycles:\s+(?P<cycles>[0-9]+),\s+Operations:\s+(?P<operations>[0-9]+),\s+Operations\/Cycle:\s+(?P<opovercyc>[0-9.]+)\n')
MODEL_NAME_MATCH = re.compile(r'Model:\t(.+)')
NUM_MODELS = 33
GT_predictions = {0: 42, 1: 77, 2: 42, 3: 67, 4: 42, 5: 121, 6: 311, 7: 77, 8: 78, 9: 69, 10: 42, 11: 311, 12: 77, 13: 39, 14: 121, 15: 121, 16: 49, 17: 42, 18: 42, 19: 43, 20: 42, 21: 42, 22: 42, 23: 42, 24: 42, 25: 42, 26: 77, 27: 42, 28: 42, 29: 42, 30: 39, 31: 276, 32: 42}
# predicted values with emul mode (tested to be ok in validation) on ILSVRC2012_val_00011158 image

def timeout_handler(signum, frame):
	raise Exception("end of time")

def get_performance_dict():
	performance_df = pd.read_csv('benchmark.csv', sep="\t", header=0)
	return performance_df.to_dict()

def main():
	try:
		TARGET_PLATFORM = os.environ['PLPTEST_PLATFORM']
	except:
		TARGET_PLATFORM = 'gvsoc'
	print("Target Platform: ", TARGET_PLATFORM)
	starting_model_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
	final_model_id = int(sys.argv[2]) if len(sys.argv) > 2 else NUM_MODELS

	out_predictions = {}
	for ne16, float16, hwc in [(1, 0, 0)]: #(0, 1, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0)]:
		for model_id in range(starting_model_id, final_model_id):
			model_name = str(model_id)
			signal.signal(signal.SIGALRM, timeout_handler)
			TIMEOUT = 700
			signal.alarm(TIMEOUT) # break after 200 s
			try:
				shell_command = f'make clean_model all run platform={TARGET_PLATFORM} MODEL_ID={model_id} MODEL_FP16={float16} MODEL_HWC={hwc} MODEL_NE16={ne16} PMSIS_OS=pulpos'
				print(shell_command)
				stream = os.popen(shell_command)
				platform_log = stream.readlines()
			except Exception:
				print("Out of time Exception: Model did not end the execution in the TIMEOUT = {}".format(TIMEOUT))
				platform_log = []

			platform_prediction = None
			platform_performance = (None, None)
			for line in platform_log:
				m = CLASS_MATCH.search(line)
				m_perf = PERF_MATCH.search(line)
				m_model = MODEL_NAME_MATCH.search(line)
				if m_perf:
					platform_performance = (int(m_perf['cycles']), float(m_perf['opovercyc']))
				if m:
					platform_prediction = int(m['class'])
				if m_model:
					model_name = m_model[0]

			model_name += ('_float16' if float16 else '') + ('_hwc' if hwc else '') + ('_ne16' if ne16 else '')

			stream_tflite = os.popen('make test_tflite MODEL_ID={}'.format(model_id))
			tflite_log = stream_tflite.readlines()
			tflite_prediction = None
			for line in tflite_log:
				m = CLASS_MATCH.search(line)
				if m:
					tflite_prediction = int(m['class'])
					break

			TEST = "OK" if platform_prediction == GT_predictions[model_id] else "FAIL"

			out_predictions.update({model_name: [platform_prediction, GT_predictions[model_id], tflite_prediction, platform_performance[0], platform_performance[1], TEST]})
			for k, v in out_predictions.items():
				print("MODEL: {} OUT: {}".format(k, v))

	df = pd.DataFrame.from_dict(out_predictions, orient='index', columns=['platform', 'ground truth', 'tflite', 'Cycles', 'Mac/Cyc', 'passed'])
	pd.set_option('display.max_columns', 8)
	print(df)
	update_performance_dict(df)
	failed_models = [k for k, v in out_predictions.items() if v[-1] == "FAIL"]
	if len(failed_models) > 0:
		print("Failing models: ", failed_models)
		return 1
	return 0

if __name__ == "__main__":
	main()
