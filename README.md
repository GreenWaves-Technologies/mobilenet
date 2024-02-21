# MobileNet on GAP

This repository showcases the GAP*flow* for Image Classification models inference trained on ImageNet Dataset with the 3 different families of [MobileNet](https://arxiv.org/abs/1704.04861) NN Architecture. 
Specifically, the GAP*flow* code generation applies on quantized state-of-the-art deep models in TFLite format for [visual object classification](https://www.tensorflow.org/lite/guide/hosted_models).
Besides the *nntool* scripts needed to import TFLite graph, we include the application code to run inference on [gvsoc](https://greenwaves-technologies.com/gvsoc-the-full-system-simulator-for-profiling-gap-applications/) or [GAP9 boards](https://greenwaves-technologies.com/store/).

The code is intended as a fast-access point to Greenwaves Technologies tools for model bechmarking and as a starting point for development of edge intelligence on GAP9.

## Supported Models
Below the models tested with the GAP*flow* (FPS and Top 1 Accuracy has been collected using the accelerator - MODEL_NE16 setting activated).

| MODEL ID | Quantized TFLite Graph                                                                                                            | MACs (M) | Parameters (M) | Top 1 Accuracy | MAC/Cyc | Energy (mJ) |
|----------|-----------------------------------------------------------------------------------------------------------------------------------|----------|----------------|----------------|---------|-------------|
|        0 |[MobileNet V1 224 1.0](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_1.0_224_quant.tgz)               |      569 |           4.24 |           70.1 |    34.8 |             |	
|        1 |[MobileNet V1 192 1.0](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_1.0_192_quant.tgz)               |      418 |           4.24 |           69.2 |    34.8 |             |	
|        2 |[MobileNet V1 160 1.0](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_1.0_160_quant.tgz)               |      291 |           4.24 |           67.2 |    28.2 |             |	
|        3 |[MobileNet V1 128 1.0](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_1.0_128_quant.tgz)               |      186 |           4.24 |           63.4 |    23.3 |             |
|        4 |[MobileNet V1 224 0.75](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.75_224_quant.tgz)             |      317 |           2.59 |           66.8 |    33.0 |             |	
|        5 |[MobileNet V1 192 0.75](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.75_192_quant.tgz)             |      233 |           2.59 |           66.1 |    33.5 |             |	
|        6 |[MobileNet V1 160 0.75](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.75_160_quant.tgz)             |      162 |           2.59 |           62.3 |    27.9 |             |	
|        7 |[MobileNet V1 128 0.75](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.75_128_quant.tgz)             |      104 |           2.59 |           55.8 |    24.8 |             |	
|        8 |[MobileNet V1 224 0.5](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.5_224_quant.tgz)               |      150 |           1.34 |           60.7 |    26.9 |             |	
|        9 |[MobileNet V1 192 0.5](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.5_192_quant.tgz)               |      110 |           1.34 |           60.0 |    27.9 |             |	
|       10 |[MobileNet V1 160 0.5](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.5_160_quant.tgz)               |       77 |           1.34 |           57.7 |    23.9 |             |	
|       11 |[MobileNet V1 128 0.5](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.5_128_quant.tgz)               |       49 |           1.34 |           54.5 |    22.5 |             |	
|       12 |[MobileNet V1 224 0.25](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.25_224_quant.tgz)             |       41 |           0.47 |           48.0 |    16.3 |             |	
|       13 |[MobileNet V1 192 0.25](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.25_192_quant.tgz)             |       34 |           0.47 |           46.0 |    16.9 |             |	
|       14 |[MobileNet V1 160 0.25](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.25_160_quant.tgz)             |       21 |           0.47 |           43.4 |    15.3 |             |	
|       15 |[MobileNet V1 128 0.25](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.25_128_quant.tgz)             |       14 |           0.47 |           39.5 |    15.1 |             |	
|       16 |[MobileNet V2 224 1.4](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_224_140.tgz)                           |      582 |           6.06 |           75.0 |    17.8 |             |	
|       17 |[MobileNet V2 224 1.0](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_224_100.tgz)                           |      300 |           3.47 |           71.8 |    16.7 |             |	
|       18 |[MobileNet V2 192 1.0](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_192_100.tgz)                           |      221 |           3.47 |           70.7 |         |             |	
|       19 |[MobileNet V2 160 1.0](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_160_100.tgz)                           |      154 |           3.47 |           68.8 |         |             |	
|       20 |[MobileNet V2 128 1.0](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_128_100.tgz)                           |       56 |           3.47 |           60.3 |         |             |	
|       21 |[MobileNet V2 96 1.0](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_96_100.tgz)                             |       99 |           3.47 |           65.3 |    13.9 |             |	
|       22 |[MobileNet V2 224 0.75](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_224_75.tgz)                           |      209 |           2.61 |           71.8 |         |             |	
|       23 |[MobileNet V2 192 0.75](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_192_75.tgz)                           |      153 |           2.61 |           70.7 |    18.8 |             |	
|       24 |[MobileNet V2 160 0.75](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_160_75.tgz)                           |      107 |           2.61 |           68.8 |         |             |	
|       25 |[MobileNet V2 128 0.75](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_128_75.tgz)                           |       69 |           2.61 |           65.3 |    15.9 |             |	
|       26 |[MobileNet V2 96 0.75](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_96_75.tgz)                             |       39 |           2.61 |           58.8 |    14.3 |             |	
|       27 |[MobileNet V2 224 0.5](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_224_50.tgz)                            |       97 |           1.95 |           71.8 |    15.3 |             |	
|       28 |[MobileNet V2 192 0.5](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_192_50.tgz)                            |       71 |           1.95 |           70.7 |    15.4 |             |	
|       29 |[MobileNet V2 160 0.5](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_160_50.tgz)                            |       50 |           1.95 |           68.8 |         |             |	
|       30 |[MobileNet V2 128 0.5](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_128_50.tgz)                            |       32 |           1.95 |           65.3 |    11.6 |             |	
|       31 |[MobileNet V2 96 0.5](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_96_50.tgz)                              |       18 |           1.95 |           75.8 |    10.3 |             |	
|       32 |[MobileNet V3 Large Minimalistic](https://storage.googleapis.com/mobilenet_v3/checkpoints/v3-large-minimalistic_224_1.0_uint8.tgz) |      209 |            3.9 |           71.3 |    18.9 |             |


## Download the models
A Mobilenet TFLite model can be found in the models/tflite_models folder. 
To download other tflite hosted models you can run the script:

	./models/download_models.sh

# Requirements

* [GAPsdk](https://github.com/GreenWaves-Technologies/gap_sdk) 5.5+ 

# Project structure
- [main.c](main.c): application code running on GAP9 for fixed point inference
- [main_fp16.c](main.c): application code running on GAP9 for float16 inference
- [images](images): contains sample images for each input_size model.
- [models](models):
	- nntool_scripts: here you can find the nntool scripts used for the AT model generation. Both the old nntool scripting for command line interface usage (obsolete), and the python api usage with direct python scripting (`models/nntool_scripts/nntool_api.py`);
	- tflite_models: the CMake build structure suppose the tflite models files in this directory;
	- download_models.sh: the script to automatically download all the tflite quantized hosted models.
- [common.cmake](common.cmake): defines the topology parameters which will be passed as macro defines to your application code.

# How to run

This project is CMake based, you can use `menuconfig` to select the different available options (type of quantization, model architecture, but also sdk options like target board/gvsoc, frequency settings, etc..) by default the model run will be a MobileNetV1 224_1.0 with NE16 quantization (per channel int8 weights / int8 activations):

	mkdir build
	cd build
	cmake ../
	make menuconfig (to choose the different options)
	make run -j

## Power Analysis on GAP9

Every model has been tested on GAP9 chip to evaluate performance and power consumption. The devise used is a picoscope 4444

# NOTE

- Makefile is deprecated in the latest SDK. Left here for back compatibility but not supported anymore.
