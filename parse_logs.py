import pandas as pd
import glob
import re
from nntool.api import CompletedProcess

def get_id_from_filename(filename):
	return int(filename.split("mobilenet_id_")[-1].split("_")[0])

match_model = re.compile(r'Model:\s+(.+)\n')
match_class = re.compile(r'Predicted class:\s+(.+)\n')
match_perf  = re.compile(r' *Total: *Cycles: +(\d+)[^:]+: +(\d+.\d+)[^:]+: +(\d+)[^:]+: +(\d+.\d+)[^:]+: +([\d<.]+|nan)')

# results = {get_id_from_filename(file): {} for file in glob.glob("log_meas/*perf*")}
results = []
for file in glob.glob("log_meas/*perf*"):
	class_num = cyc = op = op_cyc = 0
	for line in open(file, "r"):
		m_model = match_model.search(line)
		if m_model:
			model_name = m_model.group(1)
			continue
		m_class = match_class.search(line)
		if m_class:
			class_num = m_class.group(1)
			continue
		m_perf = match_perf.search(line)
		if m_perf:
			cyc = m_perf.group(1)
			op = m_perf.group(3)
			op_cyc = m_perf.group(5)
			continue

	at_log_file = file.split("perf")[0] + "at.log"
	at_log = ""
	with open(at_log_file, "r") as f:
		at_log = f.read()
	res = CompletedProcess(
		returncode=0,
		stdout=at_log,
	)

	row = {
		"id": int(file.split("mobilenet_id_")[-1].split("_")[0]),
		"model_name": model_name,
		"freq": int(file.split("_")[-1].split("MHz")[0]),
		"pred_class": class_num,
		"cyc": cyc,
		"op": op,
		"op_cyc": op_cyc,
	}
	row.update(res.basic_mem_infos)
	results.append(row)

df = pd.DataFrame(results)
df = df.sort_values(by=["id", "freq"])
df.to_csv("results.csv", index=False)
