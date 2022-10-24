import os
import sys
from nntool_python_utils.imagenet_utils import test_imagenet_nntool
from nntool.api import NNGraph
import logging

model_path = sys.argv[1]
model_name, ext = os.path.splitext(model_path)
model_name = os.path.split(model_name)[-1]
dataset_path = sys.argv[2]
print(f"testing model {model_path} on dataset {dataset_path} -> logging to {model_name}")

if len(sys.argv) > 3:
    ne16 = sys.argv[3] == "ne16"
    fp16 = sys.argv[3] == "fp16"
else:
    ne16 = True
    fp16 = False

G = NNGraph.load_graph(model_path, load_quantization=ext == ".tflite")
if ext != ".json":
    G.adjust_order()
    G.fusions("scaled_match_group")
    stats = None
    G.quantize(
        stats,
        graph_options={
            "use_ne16": ne16,
            "hwc": True
        }
    )

is_ne16 = any(qrec.cache.get("ne16")  for qrec in G.quantization.values())
is_fp16 = any(qrec.ktype == "float"  for qrec in G.quantization.values())
test_imagenet_nntool(G, dataset_path, f"{model_name}_nntool{'_ne16' if is_ne16 else ('_fp16' if is_fp16 else '_sw')}.log")
