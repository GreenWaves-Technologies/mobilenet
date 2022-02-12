echo "Starting Apache web server in docker on port 8080"
docker run --rm -d -p 8080:80 -v "$PWD/htdocs":/usr/local/apache2/htdocs/ httpd:2.4-alpine

echo "Starting image server. Go to localhost:8080/detect_scoket.html to view"
python image_generator_socket.py
