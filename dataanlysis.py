import csv
import sys
import numpy as np

csv.field_size_limit(20000000)

cluster = []
soc = []
memory = [] 
with open('test.csv', newline='') as f:
	reader = csv.reader(f,quoting=csv.QUOTE_NONNUMERIC)
	for r, row in enumerate(reader):
		if r == 0:
			print("Reading cluster data")
			cluster = np.array(row)
		elif r == 1:
			print("Reading soc data")
			soc = np.array(row)			
		elif r == 2:
			print("Reading memory data")
			memory = np.array(row)	
		else:
			print("Reading extra lines")

print(cluster)
print(np.average(cluster))
print(np.average(soc))
print(np.average(memory))