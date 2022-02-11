sudo docker run -it --rm \
    --network host \
    --privileged \
    -v $PWD:/root/gap_runner \
    gap_sdk \
    python -u /root/gap_runner/gap_server.py
    #bash
    
