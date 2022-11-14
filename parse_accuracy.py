from glob import glob
import sys
import re
import csv
import os

matcher = re.compile(r'.*Class: \[1000\/1001\] Time: \d+.\d+ \(\d+.\d+\) Acc@1: \d+.\d+ \((\d+.\d+)\) Acc@5: \d+.\d+ \((\d+.\d+)\)')
name_matcher = re.compile(r'(\S+)_quant_(\S+).log')

results = {}
with open('acc_results.csv', 'w', newline='') as csvfile:
	spamwriter = csv.writer(csvfile, delimiter=',')

	for file in glob(sys.argv[1] + "*"):
		match_name = name_matcher.search(file)
		if not match_name:
			print(f"cannot parse {file} filename")
			continue

		acc1 = 0
		acc5 = 0
		for line in open(file, "r"):
			match = matcher.search(line)
			if match:
				acc1 = float(match.group(1))
				acc5 = float(match.group(2))
				break
		if not acc1:
			continue

		model_name = os.path.split(match_name.group(1))[1]
		model_type = match_name.group(2)
		if model_name in results:
			results[model_name].update({model_type: {"acc1": acc1, "acc5": acc5}})
		else:
			results[model_name] = {model_type: {"acc1": acc1, "acc5": acc5}}

		if acc1:
			spamwriter.writerow([model_name, model_type, acc1, acc5])

	for k, v in results.items():
		print(k)
		print("\tNE16", v.get("nntool_ne16"))
		print("\tFP16", v.get("nntool_fp16"))

