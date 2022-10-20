import os
import numpy as np
import glob
import re

match_model = re.compile(r'Model:\s+(.+)\n')
match_class = re.compile(r'Predicted class:\s+(.+)\n')
match_perf  = re.compile(r'\s+Total:\s+Cycles:\s+(\d+),\s+Operations:\s+(\d+),\s+Operations\/Cycle:\s+(\d*.?\d*)\n')
match_nntool_class = re.compile(r'Nntool Predict:\s+(.+)\n')

results = []
for file in glob.glob("logs/log_*"):
	model_id = int(re.split('_|\.', file)[3])
	fp16 = int(re.split('_|\.', file)[-2])
	ne16 = int(re.split('_|\.', file)[-4])
	for line in open(file, "r"):
		m_model = match_model.search(line)
		if m_model:
			model_name = m_model.group(1) + ("_ne16" if ne16 else ("_fp16" if fp16 else ""))
			continue
		m_class = match_class.search(line)
		if m_class:
			class_num = m_class.group(1)
			continue
		m_perf = match_perf.search(line)
		if m_perf:
			cyc = m_perf.group(1)
			op = m_perf.group(2)
			op_cyc = m_perf.group(3)
			continue
		m_nntool_class = match_nntool_class.search(line)
		if m_nntool_class:
			nntool_class_num = m_nntool_class.group(1)
			continue
	results.append((model_id, model_name, class_num, nntool_class_num, cyc, op, op_cyc))

for el in results:
	print(el)

