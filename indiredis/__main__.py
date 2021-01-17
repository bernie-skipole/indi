
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

from indi_mr import inditoredis, indi_server, redis_server

# any wsgi web server can serve the wsgi application produced by make_wsgi_app,
# in this example the web server 'waitress' is used

from waitress import serve

from . import make_wsgi_app


version = "0.3.1"

if __name__ == "__main__":


    parser = argparse.ArgumentParser(usage="python3 -m indiredis [options] blobdirectorypath",
        description="INDI web client communicating to indiserver and saving data to redis and to a BLOB directory.")
    parser.add_argument("blobdirectorypath", help="Path of the directory where BLOB's will be set")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port of the web service (default 8000).")
    parser.add_argument("--iport", type=int, default=7624, help="Port of the indiserver (default 7624).")
    parser.add_argument("--ihost", default="localhost", help="Hostname of the indiserver (default localhost).")
    parser.add_argument("--rport", type=int, default=6379, help="Port of the redis server (default 6379).")
    parser.add_argument("--rhost", default="localhost", help="Hostname of the redis server (default localhost).")
    parser.add_argument("--prefix", default="indi_", help="Prefix applied to redis keys (default indi_).")
    parser.add_argument("--toindipub", default="to_indi", help="Redis channel used to publish data to indiserver (default to_indi).")
    parser.add_argument("--fromindipub", default="from_indi", help="Redis channel on which data is published from indiserver (default from_indi).")
    parser.add_argument("--version", action="version", version=version)
    args = parser.parse_args()

    # define the hosts/ports where servers are listenning, these functions return named tuples
    # which are required as arguments to inditoredis() and to make_wsgi_app()

    indi_host = indi_server(host=args.ihost, port=args.iport)
    redis_host = redis_server(host=args.rhost, port=args.rport, db=0, password='', keyprefix=args.prefix,
                              to_indi_channel=args.toindipub, from_indi_channel=args.fromindipub)


    # create a wsgi application
    application = make_wsgi_app(redis_host, args.blobdirectorypath, url='/')
    if application is None:
        print("ERROR: Are you sure the skipole framework is installed?")
        sys.exit(1)

    ###################### Remove for deployment ##################################
    #                                                                              #
    #from skipole import skiadmin, set_debug                                       #
    #set_debug(True)                                                               #
    #skiadmin_application = skiadmin.makeapp(editedprojname='webdemo')             #
    #application.add_project(skiadmin_application, url='/skiadmin')                #
    #                                                                              #
    ###############################################################################

    # serve the application with the python waitress web server in another thread
    webapp = threading.Thread(target=serve, args=(application,), kwargs={'host':'localhost', 'port':args.port})
    webapp.start()

    # and start the blocking function inditoredis
    inditoredis(indi_host, redis_host, log_lengths={}, blob_folder=args.blobdirectorypath)

