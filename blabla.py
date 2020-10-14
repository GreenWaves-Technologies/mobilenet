import pandas as pd
import csv

GT_performance = {0: 6.75633, 1: 6.958425, 2: 7.767089, 3: 7.671721, 4: 7.456866, 5: 7.5372, 6: 7.676829, 7: 7.449675, 8: 7.125032, 9: 7.084658, 10: 7.278495, 11: 6.427716, 12: 6.063097, 13: 5.876167, 14: 5.601814, 15: 5.282983, 16: 4.527786, 17: 5.913087, 18: 5.981472, 19: 5.727079, 20: 5.791325, 21: 5.313634, 22: 5.585749, 23: 5.406378, 24: 5.62603, 25: 5.200447, 26: 4.97893, 27: 4.864435, 28: 4.80691, 29: 4.626174, 30: 4.272549, 31: 3.602734, 32: 5.016086}

df = pd.DataFrame.from_dict(GT_performance, orient='index', columns=['SDK3.5: FC=250MHz CL=175MHz'])
df.to_csv("performance.csv", index_label="MODEL_ID", sep="\t")

with open('performance.csv', "r") as f:
	reader = csv.reader(f, delimiter='\t')
	for i, row in enumerate(reader):
		if i==0:
			header = row
			dict_out = {key: {} for key in header[1:]}
			continue
		for key in header[1:]:
			dict_out[key].update({row[0]: row[1]})
	print(dict_out['SDK3.5: FC=250MHz CL=175MHz'])

df2 = pd.read_csv('performance.csv', sep="\t", header=0)
df3 = df2.columns[1]
df2['new_column'] = list(range(33))
print(df2['SDK3.5: FC=250MHz CL=175MHz'].to_list())
print(df2)