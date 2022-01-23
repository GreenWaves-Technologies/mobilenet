sudo docker run -it --rm \
    --network host \
    --privileged \
    -v $PWD:/root/gap_runner \
    nvcr.io/nvidia/l4t-ml:r32.5.0-py3 \
    python3 -u /root/gap_runner/nano_server.py
