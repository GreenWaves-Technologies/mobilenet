echo "Starting Apache web server in docker on port 8080"
docker run --rm -d -p 8080:80 -v "$PWD/htdocs":/usr/local/apache2/htdocs/ httpd:2.4-alpine

hostname=`hostname`

echo "Starting image server. Go to $hostname:8080 to view"
python img_server.py
