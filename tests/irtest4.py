import threading, os, sys

from indiredis import driverstoredis, redis_server, indiwsgi

# any wsgi web server can serve the wsgi application produced by
# indiwsgi.make_wsgi_app, in this example the web server 'waitress' is used

from waitress import serve

# define the hosts/ports where servers are listenning, these functions return named tuples
# which are required as arguments to inditoredis() and to indiwsgi.make_wsgi_app()

redis_host = redis_server(host='localhost', port=6379)

# Set a directory of your choice where blobs will be stored
BLOBS = '/path/to/blob_folder'

# create a wsgi application
application = indiwsgi.make_wsgi_app(redis_host, blob_folder=BLOBS)
if application is None:
    print("Are you sure the skipole framework is installed?")
    sys.exit(1)

# serve the application with the python waitress web server in its own thread
webapp = threading.Thread(target=serve, args=(application,), kwargs={'host':'127.0.0.1', 'port':8000})
# and start it
webapp.start()

# and start driverstoredis
driverstoredis(["indi_simulator_telescope", "indi_simulator_ccd"], redis_host, blob_folder=BLOBS)

