# Image Classification Models on GAP

In this repository you will find the usage of the GAP*flow* on the set of quantized TFLite models trained on Imagenet released by Tensorflow in their [object classification Hosted Models](https://www.tensorflow.org/lite/guide/hosted_models):

| MODEL ID | Quantized TFLite Graph | MACs (M) | Parameters (M) | Top 1 Accuracy | GAP8 Time (ms [cyc]) |
|-----|------------------------|----------|----------------|----------------|----------------------|
| 0        |[MobileNet V1 224 1.0](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_1.0_224_quant.tgz)  | 569 | 4.24 | 70.1 | XX |
| 1        |[MobileNet V1 192 1.0](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_1.0_192_quant.tgz)  | 418 | 4.24 | 69.2 | XX |
| 2        |[MobileNet V1 160 1.0](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_1.0_160_quant.tgz)  | 291 | 4.24 | 67.2 | XX |
| 3        |[MobileNet V1 128 1.0](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_1.0_128_quant.tgz)  | 186 | 4.24 | 63.4 | XX |
| 4        |[MobileNet V1 224 0.75](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.75_224_quant.tgz)| 317 | 2.59 | 66.8 | XX |
| 5        |[MobileNet V1 192 0.75](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.75_192_quant.tgz)| 233 | 2.59 | 66.1 | XX |
| 6        |[MobileNet V1 160 0.75](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.75_160_quant.tgz)| 162 | 2.59 | 62.3 | XX |
| 7        |[MobileNet V1 128 0.75](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.75_128_quant.tgz)| 104 | 2.59 | 55.8 | XX |
| 8        |[MobileNet V1 224 0.5](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.5_224_quant.tgz)  | 150 | 1.34 | 60.7 | XX |
| 9        |[MobileNet V1 192 0.5](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.5_192_quant.tgz)  | 110 | 1.34 | 60.0 | XX |
| 10       |[MobileNet V1 160 0.5](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.5_160_quant.tgz)  | 77  | 1.34 | 57.7 | XX |
| 11       |[MobileNet V1 128 0.5](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.5_128_quant.tgz)  | 49  | 1.34 | 54.5 | XX |
| 12       |[MobileNet V1 224 0.25](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.25_224_quant.tgz)| 41  | 0.47 | 48.0 | XX |
| 13       |[MobileNet V1 192 0.25](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.25_192_quant.tgz)| 34  | 0.47 | 46.0 | XX |
| 14       |[MobileNet V1 160 0.25](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.25_160_quant.tgz)| 21  | 0.47 | 43.4 | XX |
| 15       |[MobileNet V1 128 0.25](http://download.tensorflow.org/models/mobilenet_v1_2018_08_02/mobilenet_v1_0.25_128_quant.tgz)| 14  | 0.47 | 39.5 | XX |
| 16	   |[MobileNet V3 Large Minimalistic](https://storage.googleapis.com/mobilenet_v3/checkpoints/v3-large-minimalistic_224_1.0_uint8.tgz)| 209 | 3.9 | 71.3 | XX |
| 17       |[MobileNet V2 224 1.4](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_224_140.tgz)              | 582 | 6.06 | 75.0 | XX |
| 18       |[MobileNet V2 224 1.0](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_224_100.tgz)              | 300 | 3.47 | 71.8 | XX |
| 19       |[MobileNet V2 192 1.0](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_192_100.tgz)              | 221 | 3.47 | 70.7 | XX |
| 20       |[MobileNet V2 160 1.0](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_160_100.tgz)              | 154 | 3.47 | 68.8 | XX |
| 21       |[MobileNet V2 128 1.0](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_128_100.tgz)              | 56  | 3.47 | 60.3 | XX |
| 22       |[MobileNet V2 96 1.0](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_96_100.tgz)                | 99  | 3.47 | 65.3 | XX |
| 23       |[MobileNet V2 224 0.75](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_224_75.tgz)              | 209 | 2.61 | 71.8 | XX |
| 24       |[MobileNet V2 192 0.75](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_192_75.tgz)              | 153 | 2.61 | 70.7 | XX |
| 25       |[MobileNet V2 160 0.75](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_160_75.tgz)              | 107 | 2.61 | 68.8 | XX |
| 26       |[MobileNet V2 128 0.75](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_128_75.tgz)              | 69  | 2.61 | 65.3 | XX |
| 27       |[MobileNet V2 96 0.75](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_96_75.tgz)                | 39  | 2.61 | 58.8 | XX |
| 28       |[MobileNet V2 224 0.5](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_224_50.tgz)               | 97  | 1.95 | 71.8 | XX |
| 29       |[MobileNet V2 192 0.5](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_192_50.tgz)               | 71  | 1.95 | 70.7 | XX |
| 30       |[MobileNet V2 160 0.5](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_160_50.tgz)               | 50  | 1.95 | 68.8 | XX |
| 31       |[MobileNet V2 128 0.5](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_128_50.tgz)               | 32  | 1.95 | 65.3 | XX |
| 32       |[MobileNet V2 96 0.5](https://storage.googleapis.com/mobilenet_v2/checkpoints/quantized_v2_96_50.tgz)                 | 18  | 1.95 | 75.8 | XX |

## Requirements

The porting process exploit the entire CNN GAP*flow* released in the GAPsdk 3.5+ release.

## Project structure

- [common](common):
	- headers: contains the header files needed by the functions generated by the AutoTiler for each model;
	- model_rules.mk: contains the common rules to control the GAP*flow* with makefiles;
	- model_decl.mk: defines the common paths needed for the model and GAP*flow* compilation and run;
- [images](images): contains sample images for each input_size model.
- [models](models):
	- nntool_scripts: here you can find the nntool scripts used for the AT model generation. For MobileNet V1 and V2 we developed specific nntool scripts which leverage the Autotiler features to optimize the performances;
	- tflite_models: the makefile structure suppose the tflite models files in this directory;
	- download_models.sh: the script to automatically download all the tflite quantized hosted models.
- validation_on_emul: this folder contains everything related to the accuracy check of the model on the target GAP chip. It uses the \_\_EMUL\_\_ mode supported by the GAP*flow*. The usage of this tool is explained in its relative directory [documentation](validation_on_emul/README.md).
- [common.mk](common.mk): defines the topology parameters which will be passed as macro defines to your application code.
- [main.c](main.c): contains the main application that will be run on the platform.

## Download the models

To lighten the repository, this project comes with only one tflite network (MobileNetV1 input_size=224 alpha=1.0) inside the models/tflite_models directory. To download all the models from tflite hosted models you have to run:

	cd models
	./download_script.sh

## Inference On Chip

Once you downloaded your model and sourced the GAPsdk, you can run the main application on chip (or platform simulator *gvsoc*) with:

	make clean all run [platform=gvsoc] MODEL_ID=XX FREQ_FC=YY FREQ_CL=ZZ [HAVE_CAMERA=1 HAVE_LCD=1]

set the MODEL_ID accordingly to your target model. The FREQ_FC and FREQ_CL are, respectively, the Fabric Controllers and Clusters frequencies expressed in Hz.

If HAVE_CAMERA is not set the application will run on a [sample image](images) (the right one accordingly to the input_size of the model) flashed to the board from your PC filesystem.
