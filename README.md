# GAP Runner

## Preliminaries
- Build the container defined in gap/docker/gap_sdk.Dockerfile
  - Note that the GAP SDK requires a processor that supports RISC-V
- If we need websockets, build the container defined in nano/docker/nano.Dockerfile
  - If not than the base image from NVIDIA should be okay
- The Arduino code is gap/spi-wifi/spi_slave/spi_slave.ino
  - Change the SSID / password fields if needed
  - See gap/spi-wifi/README.md for more info

## Running
- Start the web server by running ./web/run.sh
- Press reset button on ESP8266 module
- Start the nano server by running ./nano/run.sh
  - I use tmux to run the two nano processes at the same time
- Once the nano shows the connection is successful, start the GAP8 part by running ./gap/run.sh
- View the output at NANO_IP:8080 on any web browser on the network

## Limitations
- Currently the image and 8 hidden channels are always sent
  - The control singal sent to the GAP8 is just random bytes
  - In theory, it should be easy to change this

## TODO
- Get the GAP8 to boot on its own
- Tweak poll frequency in web server javascript
  - Currently every 200 ms (i.e. 5 FPS)
  - As fast as 33 ms (30 FPS) as worked for me, but unstable
- Tune detector runtime settings (deployment dependent)
  - Min score threshold (trt_detector.py line 80)
  - NMS IoU threshold (trt_detector.py line 88)
  - Min score to display (inference.py line 29)
  - Remove unneeded classes?
  - Adjust camera for lightning
     - Reset AEG / histrogram equalization 
