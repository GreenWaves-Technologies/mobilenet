import numpy as np
from execution.graph_executer import GraphExecuter
from execution.quantization_mode import QuantizationMode
from utils.data_importer import import_data
from graph.types import ImageFormatParameters

in_node = [node for node in G.input_nodes()][0]
image_formatters = [node for node in G.nodes(node_classes=ImageFormatParameters)]
in_shape = in_node.in_dims[0].shape
input_image = f"images/ILSVRC2012_val_00011158_{in_shape[1]}.ppm"

in_norm_func = "x:x/128-1" if len(image_formatters) == 0 else None
transpose = len(image_formatters) > 0 and in_shape[0] == 3
input_data = import_data(input_image, norm_func=in_norm_func, transpose=transpose).astype(np.float32)
executer = GraphExecuter(G, qrecs=G.quantization)
outputs = executer.execute([input_data], qmode=QuantizationMode.all(), silent=True)
pred_class = np.argmax(outputs[-1])
print(pred_class)
with open("nntool_prediction.txt", "w") as f:
	f.write(f"Nntool Predict: {str(pred_class)}")
