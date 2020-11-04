#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

# Copyright (C) 2019 GreenWaves Technologies
# All rights reserved.

# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import argparse

import argcomplete
import os
import sys
import numpy as np
import tensorflow as tf
from PIL import Image

print('Tensorflow version: ', tf.__version__)

# Program to test the tflite inference on a single image
# Example of usage:
# 	python3 -t tflite_models/mobilenet_v1_1_0_224_quant.tflite \
#			-i ../images/ILSVRC2012_val_00011158_224.ppm \
#			-P [to print the output]


def create_parser():
	# create the top-level parser
	parser = argparse.ArgumentParser(prog='tflite_inference')

	parser.add_argument('-t', '--tflite_model',
						help="path to tflite model to test")
	parser.add_argument('-i', '--input_image',
						help="path to image to test")
	parser.add_argument('-M', '--image_mode',
						default='RGB',
						help="image input format")
	parser.add_argument('-P', '--print_output',
						action='store_true',
						help="print output tensor")
	return parser

def main():
	parser = create_parser()
	argcomplete.autocomplete(parser)
	args = parser.parse_args()

	if not args.tflite_model:
		raise ValueError()
	interpreter = tf.lite.Interpreter(model_path=args.tflite_model)
	interpreter.allocate_tensors()
	
	# Get input and output tensors.
	input_details = interpreter.get_input_details()
	output_details = interpreter.get_output_details()
	print('Input details: ', input_details)
	print('Output details: ', output_details)
	
	#read image and resize
	img = Image.open(args.input_image)
	img = img.resize((input_details[0]['shape'][1], input_details[0]['shape'][2]))
	input_array = np.array(img, dtype=np.uint8)
	input_array = np.reshape(input_array, input_details[0]['shape']).astype(np.uint8)
	
	#set interpreter tensor and invoke
	interpreter.set_tensor(input_details[0]['index'], input_array)
	interpreter.invoke()
	output = interpreter.get_tensor(output_details[0]['index'])
	print("Predicted class:\t{}\nWith confidence:\t{}".format(np.argmax(output), output[0, np.argmax(output)]))
	if args.print_output:
		np.set_printoptions(threshold=sys.maxsize)
		print("Predictions: ")
		print(output)

if __name__ == '__main__':
    main()
