import argcomplete
from nntool_python_utils.imagenet_utils import test_imagenet_nntool
from nntool_scripts.nntool_api import build_nntool_graph, create_model_parser

if __name__ == "__main__":
    parser = create_model_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    G = build_nntool_graph(
        args.trained_model,
        args.quant_type,
    )
    G.name = "mobilenet"
    test_imagenet_nntool(G, args.dataset_path, f"{args.trained_model}_nntool{args.quant_type}.log")
