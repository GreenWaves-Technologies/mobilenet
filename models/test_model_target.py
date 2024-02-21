import os
import argcomplete
from nntool_scripts.nntool_api import build_nntool_graph, create_model_parser
from nntool.api.utils import quantization_options, model_settings
from PIL import Image
import numpy as np

if __name__ == "__main__":
    
    parser = create_model_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    G = build_nntool_graph(
        args.trained_model,
        args.quant_type,
    )
    G.name = "mobilenet"

    inp = Image.open("images/ILSVRC2012_val_00011158_224.ppm")
    inp = np.array(inp)
    qout = G.execute([inp], dequantize=False, quantize=True)

    G[0].at_options.allocate = 1
    expressions_file_name = os.path.splitext(os.path.split(args.expressions_file_path)[-1])[0]
    res = G.execute_on_target(
        input_tensors=qout[0],
        directory="test_model",
        check_on_target=True,
        print_output=True,
        settings=model_settings(
            tensor_directory=args.tensors_dir,
            model_directory=os.path.split(args.at_model_path)[0],
            model_file=os.path.split(args.at_model_path)[1],
            l3_ram_device="AT_MEM_L3_DEFAULTRAM",
            l3_flash_device="AT_MEM_L3_DEFAULTFLASH" if args.flash_type == "flash" else "AT_MEM_L3_MRAMFLASH",
            l2_size=1300000,
            l1_size=128000,
            # graph_l1_promotion=2,
            graph_warm_construct=1,
            graph_size_opt=2,
            graph_const_exec_from_flash=True,
            graph_async_fork=True,
            privileged_l3_flash_device="AT_MEM_L3_MRAMFLASH",
            privileged_l3_flash_size=int(1.8*1024*1024),
            basic_kernel_header_file=f"{expressions_file_name}.h",
            basic_kernel_source_file=f"{expressions_file_name}.c",
        )
    )
