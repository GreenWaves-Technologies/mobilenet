if [ ! -f "$PWD/models/tflite_models/suffix.trt" ]; then
    /usr/src/tensorrt/bin/trtexec --onnx=$PWD/models/tflite_models/suffix.onnx --saveEngine=$PWD/models/tflite_models/suffix.trt --fp16 --verbose
fi

rm -rf $HOME/record/*

sudo docker run -it --rm \
    --network host \
    --privileged \
    -v $HOME/repos/gap_runner:/root/gap_runner \
    -v $HOME/record:/root/record \
    nvcr.io/nvidia/l4t-ml:r32.5.0-py3 \
    python3 -u /root/gap_runner/nano_client.py
