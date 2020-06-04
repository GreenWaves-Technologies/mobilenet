#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
import os
import re
import argparse, argcomplete

def create_parser():
	# create the top-level parser
	parser = argparse.ArgumentParser(prog='parse_output')
	parser.add_argument('emul_file',
						default="emul.txt")
	parser.add_argument('gvsoc_file',
						default="gvsoc.txt")
	parser.add_argument('model_name',
						default="mobilenet_v1_1_0_224_quant")
	parser.add_argument('out_file',
						default="test_gvsoc_emul/out.txt")
	return parser

def main():
	parser = create_parser()
	argcomplete.autocomplete(parser)
	args = parser.parse_args()

	OUT_matcher = re.compile(r'OUTPUT:\t(?P<out_nums>([0-9]+, )+)')

	emul_file = open(args.emul_file, 'r')
	line = emul_file.readline()
	while line:
		out_match = OUT_matcher.search(line)
		if out_match:
			output_tensor_emul = out_match['out_nums'].split(', ')[:-1]
			output_tensor_emul = [int(out) for out in output_tensor_emul]
			#print(output_tensor_emul, len(output_tensor_emul))
			break
		line = emul_file.readline()
	emul_file.close()

	gvsoc_file = open(args.gvsoc_file, 'r')
	line = gvsoc_file.readline()
	while line:
		out_match = OUT_matcher.search(line)
		if out_match:
			output_tensor_gvsoc = out_match['out_nums'].split(', ')[:-1]
			output_tensor_gvsoc = [int(out) for out in output_tensor_gvsoc]
			#print(output_tensor_gvsoc, len(output_tensor_gvsoc))
			break
		line = gvsoc_file.readline()
	gvsoc_file.close()

	#CHECK EQUIVALENCE
	error = False
	for em, gv in zip(output_tensor_emul, output_tensor_gvsoc):
		if not em == gv:
			error = True
			break
	str_out = '-----------------------------------------------------------------------------------------\n'
	str_out += '\t\t\tmodel\t\t' + args.model_name + '\twas:\t'
	if error:
		str_out += 'ERROR\n'
	else:
		str_out += 'OK\n'
	str_out += '-----------------------------------------------------------------------------------------\n'

	with open(args.out_file, 'a') as out_file:
		out_file.write(str_out)

if __name__ == '__main__':
	main()
