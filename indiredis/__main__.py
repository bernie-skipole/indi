#
# This script is meant to be run from the command line using
#
# python3 -m indiredis /path/to/blobfolder
#
#

"""Usage is

python3 -m indiredis /path/to/blobfolder

indiserver should already be running in a separate process, for example,
prior to running this script, in another terminal, run:
indiserver -v indi_simulator_telescope indi_simulator_dome

This script then creates the directory /path/to/blobfolder if it does not
exist, and then communicates with the indiserver on localhost port 7624 and
a redis server on localhost port 6379. It runs a web server on port 8000,
so connecting with a browser to http://localhost:8000 
should enable you to view and control the connected instruments.
"""


import sys, os, threading, argparse

############ these lines only required during development ###########
#skipole_package_location = "/home/bernard/git/skipole"
#
#if skipole_package_location not in sys.path:
#    sys.path.insert(0,skipole_package_location)
#####################################################################

from . import inditoredis, indi_server, redis_server, indiwsgi


version = "0.0.1"

if __name__ == "__main__":

    # any wsgi web server can serve the wsgi application produced by
    # indiwsgi.make_wsgi_app, in this example the web server 'waitress' is used

    from waitress import serve

    parser = argparse.ArgumentParser(usage="python3 -m indiredis [-h] [-p PORT] [--version] blobdirectorypath",
        description="INDI client communicating to indiserver on localhost port 7624, providing instrument control via a web service.")
    parser.add_argument("blobdirectorypath", help="Path of the directory where BLOB's will be set")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port of the web service (default 8000).")
    parser.add_argument("--version", action="version", version=version)
    args = parser.parse_args()
    blob_folder = args.blobdirectorypath
    port = args.port

    # define the hosts/ports where servers are listenning, these functions return named tuples
    # which are required as arguments to inditoredis() and to indiwsgi.make_wsgi_app()

    indi_host = indi_server(host='localhost', port=7624)
    redis_host = redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_',
                              to_indi_channel='to_indi', from_indi_channel='from_indi')


    # create a wsgi application
    application = indiwsgi.make_wsgi_app(redis_host, blob_folder)
    if application is None:
        print("Are you sure the skipole framework is installed?")
        sys.exit(1)

    # add skiadmin during development, and run serve in this thread
    application = indiwsgi.add_skiadmin(application)
    serve(application, host = "127.0.0.1", port=port)

    # comment out lines below during development

    # serve the application with the python waitress web server
    # webapp = threading.Thread(target=serve, args=(application,), kwargs={'host':'127.0.0.1', 'port':port})
    # and start it
    # webapp.start()

    # and start inditoredis
    # inditoredis(indi_host, redis_host, log_lengths={}, blob_folder=blob_folder)

