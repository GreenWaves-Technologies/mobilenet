import os
import sys
import re
from glob import glob
import pandas as pd

L1_GIVEN = re.compile(r'\s+Shared (?P<column>L1 Memory size) \(Bytes\)\s+: Given:\s+(?P<value>[0-9]+), Used:.*\n')
L2_GIVEN = re.compile(r'\s+(?P<column>L2 Memory size) \(Bytes\)\s+: Given:\s+(?P<value>[0-9]+), Used:.*\n')
RAM_USED = re.compile(r'\s+\D+(?P<column>Ram Memory size) \(Bytes\)\s+: Given:\s+[0-9]+, Used:\s+(?P<value>[0-9]+)\n')
FLASH_USED = re.compile(r'\s+\D+(?P<column>L2 Promoted Tensors Usage) \(Bytes\)\s+:\s+(?P<value>[0-9]+)\n')
STATIC_L2 = re.compile(r'\s+\D+(?P<column>Flash Memory size) \(Bytes\)\s+: Given:\s+[0-9]+, Used:\s+(?P<value>[0-9]+)\n')

L3_MEM_BW = re.compile(r'(?P<column>L3 Memory bandwidth for 1 graph run)\s+\:\s+(?P<value>[0-9]+)\s+Bytes\n')
L2_MEM_BW = re.compile(r'(?P<column>L2 Memory bandwidth for 1 graph run)\s+\:\s+(?P<value>[0-9]+)\s+Bytes\n')
KER_ARGS = re.compile(r'(?P<column>Sum of all Kernels arguments size)\s+\:\s+(?P<value>[0-9]+)\s+Bytes\n')
TIL_OH = re.compile(r'(?P<column>Tiling Bandwith overhead)\s+\:\s+(?P<value>[0-9.]+)\s+Move/KerArgSize\n')
L2_MEM_BW_PER = re.compile(r'(?P<column>Percentage of baseline BW for L2)\s+\:\s+(?P<value>[0-9.]+)\s+\%\n')
L3_MEM_BW_PER = re.compile(r'(?P<column>Percentage of baseline BW for L3)\s+\:\s+(?P<value>[0-9.]+)\s+\%\n')
KER_OPS = re.compile(r'(?P<column>Sum of all Kernels operations)\s+\:\s+(?P<value>[0-9]+)\s+Operations\n')
TOT_COEFFS = re.compile(r'(?P<column>Total amount of flash coefficients)\s+\:\s+(?P<value>[0-9]+)\s+Bytes\n')

matches = [STATIC_L2, L2_GIVEN, L1_GIVEN, RAM_USED, FLASH_USED, L3_MEM_BW, L2_MEM_BW, TIL_OH, KER_ARGS, L2_MEM_BW_PER, L3_MEM_BW_PER, KER_OPS, TOT_COEFFS]

gap_log_matcher = re.compile(r'.*Total: Cycles:\s+([0-9]+), Cyc%: [0-9.]+%, Operations:\s+[0-9]+, Op%: [0-9.]+%, Operations\/Cycle:\s+([0-9.]+)')

def main():
	out_dict = {}
	at_log_file = sys.argv[1]
	for line in open(at_log_file, "r"):
		for match in matches:
			m = match.search(line)
			if m:
				if m["column"] in out_dict:
					out_dict[m['column']].append(float(m['value']))
				else:
					out_dict[m['column']] = [float(m['value'])]
				continue

	gap_log_filename = sys.argv[2]
	tot_cyc = []
	op_cyc = []
	for line in open(gap_log_filename, "r"):
		m = gap_log_matcher.search(line)
		if m:
			tot_cyc.append(int(m[1]))
			op_cyc.append(float(m[2]))
			continue
	out_dict["Total Cycles"] = tot_cyc
	out_dict["Op/Cyc"] = op_cyc

	df1 = pd.DataFrame.from_dict(out_dict, orient='index')
	at_log_filename, _ = os.path.splitext(at_log_file)
	df1.to_csv(at_log_filename + ".csv")
	print(df1)

if __name__ == "__main__":
	main()
