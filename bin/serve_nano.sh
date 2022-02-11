if [ ! -f "$PWD/models/tflite_models/suffix.trt" ]; then
    /usr/src/tensorrt/bin/trtexec --onnx=$PWD/models/tflite_models/suffix.onnx --saveEngine=$PWD/models/tflite_models/suffix.trt --fp16 --verbose
fi


sudo docker run -it\
    --network host \
    --privileged \
    -v $PWD:/root/gap_runner \
    nvcr.io/nvidia/l4t-ml:r32.5.0-py3 \
    python3 -u /root/gap_runner/spi-wifi/SocketServer.py
