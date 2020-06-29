#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

# Copyright (C) 2019 GreenWaves Technologies
# All rights reserved.

# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import argparse

import argcomplete
import os
from PIL import Image
import numpy as np
import tensorflow as tf

print('Tensorflow version: ', tf.__version__)

def create_parser():
	# create the top-level parser
	parser = argparse.ArgumentParser(prog='h5_to_tflite')

	parser.add_argument('--graph_def_file',
						help="path to .pb model")
	parser.add_argument('--representative_dataset',
						help="path to images for calibration")
	parser.add_argument('--input_arrays',
						help='list of input arrays')
	parser.add_argument('--output_arrays',
						help='list of input arrays')
	parser.add_argument('--img_size',
						nargs=2,
						default=(224,224),
						help='list of input arrays')
	parser.add_argument('--get_tensors_name',
						action='store_true',
						help='get a list of tensors name in the .pb graph')
	return parser

def main():
	assert tf.__version__.startswith('1.15'), 'Tensorflow version must be 1.15.x'
	parser = create_parser()
	argcomplete.autocomplete(parser)
	args = parser.parse_args()

	if args.get_tensors_name:
		print('Tensors names:\n')
		gf = tf.GraphDef()   
		m_file = open(args.graph_def_file, 'rb')
		gf.ParseFromString(m_file.read())
		return

	print(args.graph_def_file)
	# Converting a GraphDef from file.
	converter = tf.lite.TFLiteConverter.from_frozen_graph(args.graph_def_file, [args.input_arrays], [args.output_arrays])
	converter.optimizations = [tf.lite.Optimize.DEFAULT]

	CALIBRATION_DATASET = args.representative_dataset
	IMG_SIZE = args.img_size

	def representative_dataset_gen():
		for file in os.listdir(CALIBRATION_DATASET):
			filepath = os.path.join(CALIBRATION_DATASET, file)
			if os.path.isdir(filepath):
				continue
			img = Image.open(filepath).resize(IMG_SIZE)
			img = np.array(img).astype(np.float32) / 128 - 1
			input_shape = (1, IMG_SIZE[0], IMG_SIZE[1], 3)
			yield [img.reshape(input_shape)]

	converter.representative_dataset = representative_dataset_gen
	converter.optimizations = [tf.lite.Optimize.OPTIMIZE_FOR_LATENCY]
	converter.inference_input_type = tf.int8  # or tf.uint8
	converter.inference_output_type = tf.int8  # or tf.uint8
	tflite_quant_model = converter.convert()

	model_name, _ = os.path.splitext(args.graph_def_file)
	tflite_file = model_name + '_quant.tflite'
	with open(tflite_file, 'wb') as out_file:
		out_file.write(tflite_quant_model)

if __name__ == '__main__':
    main()
