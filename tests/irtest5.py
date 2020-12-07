import threading, os, sys

from indiredis import mqtttoredis, mqtt_server, redis_server, indiwsgi

# any wsgi web server can serve the wsgi application produced by
# indiwsgi.make_wsgi_app, in this example the web server 'waitress' is used

from waitress import serve

# define the hosts/ports where servers are listenning, these functions return named tuples
# which are required as arguments to mqtttoredis() and to indiwsgi.make_wsgi_app()

mqtt_host = mqtt_server(host='localhost', port=1883)
redis_host = redis_server(host='localhost', port=6379)

# Set a directory of your choice where blobs will be stored
BLOBS = '~/indiblobs'

# create a wsgi application
application = indiwsgi.make_wsgi_app(redis_host, blob_folder=BLOBS)
if application is None:
    print("Are you sure the skipole framework is installed?")
    sys.exit(1)

# serve the application with the python waitress web server in its own thread
webapp = threading.Thread(target=serve, args=(application,), kwargs={'host':'127.0.0.1', 'port':8000})
# and start it
webapp.start()

# and start mqtttoredis
mqtttoredis('indi_client01', mqtt_host, redis_host, blob_folder=BLOBS)

