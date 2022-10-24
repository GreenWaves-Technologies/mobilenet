import os
import sys
from nntool_python_utils.imagenet_utils import test_imagenet_tflite, get_synset_dict

model_path = sys.argv[1]
model_name = os.path.splitext(model_path)[0]
dataset_path = sys.argv[2]
print(f"testing model {model_path} on dataset {dataset_path}")
test_imagenet_tflite(model_path, dataset_path, f"{model_name}_tflite.log")
