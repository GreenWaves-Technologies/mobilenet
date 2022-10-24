import numpy as np
import sys
from nntool.api import NNGraph
from nntool.api.utils import import_data
from nntool.graph.types import ConstantInputNode

graph_path = sys.argv[1]
G = NNGraph.load_graph(graph_path, load_quantization=".json" not in graph_path)

in_node = [node for node in G.input_nodes()][0]
in_shape = in_node.in_dims[0].shape
input_image = f"images/ILSVRC2012_val_00011158_{in_shape[1]}.ppm"

in_norm_func = "x:x/128-1"

input_data = import_data(input_image, norm_func=in_norm_func).astype(np.float32)
outputs = G.execute([input_data], quantize=True, dequantize=False)

pred_class = np.argmax(outputs[-1])
print(G.show())
print(f"Predicted class: {pred_class}")
print(f"With confidence: {outputs[-1][0][pred_class]}")
for i, out in enumerate(outputs):
	node = G[i]
	if not isinstance(node, ConstantInputNode):
		print(f"Node: S{i}: {node.name}:\n\tChecksum = {np.sum(out[0].astype(np.int8))}")
