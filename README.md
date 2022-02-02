# GAP Runner

## GUI as middle-man
The GAP8 and Nano are setup as servers over TCP. They can be restarted on their respective devices using ./serve_gap.sh and ./serve_nano.sh.

They sit waiting until the GUI starts issuing requests. This can be started (on a 3rd machine) using ./run_gui.sh. 

In this version, the message size needs to be known everywhere. For this reason, the Nano assumes that the image will be sent and all 32 channels will be sent. This will be easy to change in the future.

## GUI that reads files
This version takes the GUI out of communication loop and lets the Nano talk directly to the GAP8. The GAP8 side again starts with ./serve_gap.sh but the Nano side now uses ./client_nano.sh. The recorded frames are saved into $HOME/record as pickle files. I've tried it over my local NFS and the latency for the GUI reading the files is really bad. 
