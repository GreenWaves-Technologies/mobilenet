sudo docker run -it --rm \
    --network host \
    --privileged \
    -v $PWD:/root/gap_runner \
    gap_sdk \
    bash /root/gap_runner/bin/run_gap_wifi.sh
    #python -u /root/gap_runner/gap_server.py
    
