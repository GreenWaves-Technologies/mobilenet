#sudo service docker restart

#echo "Starting Apache web server in docker on port 8080"
#sudo docker run --rm -d \
    #-p 8080:80 \
    #-v "$PWD/htdocs":/usr/local/apache2/htdocs/ \
    #httpd:2.4-alpine

#hostname=`hostname`

#echo "Starting image server. Go to $hostname:8080 to view"
#python3 img_server.py

sudo docker run -it\
    --network host \
    --privileged \
    -v $PWD:/root/gap_runner \
    nvcr.io/nvidia/l4t-ml:r32.5.0-py3 \
    python3 -u /root/gap_runner/nano/server.py
