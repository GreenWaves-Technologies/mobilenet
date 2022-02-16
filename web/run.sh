rm -f ./web/htdocs/imgs/*

echo "Starting Apache web server in docker on port 8080"
sudo docker run --rm \
    -p 8080:80 \
    -v "$PWD/web/htdocs":/usr/local/apache2/htdocs/ \
    httpd:2.4-alpine

hostname=`hostname`
echo "Starting image server. Go to $hostname:8080 to view"
