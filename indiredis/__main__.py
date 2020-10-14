#
# This script is meant to be run from the command line using
#
# python3 -m indiredis /path/to/blobfolder
#
#


import sys, os, threading

############ these lines only required during development ###########
#skipole_package_location = "/home/bernard/git/skipole"
#
#if skipole_package_location not in sys.path:
#    sys.path.insert(0,skipole_package_location)
#####################################################################

from . import inditoredis, indi_server, redis_server, indiwsgi



DESCRIPTION = """Usage is

python3 -m indiredis /path/to/blobfolder

indiserver should already be running in a separate process, for example,
prior to running this script, in another terminal, run:
indiserver -v indi_simulator_telescope indi_simulator_dome indi_simulator_guide

This script then creates the directory /path/to/blobfolder if it does not
exist, and then communicates with the indiserver on localhost port 7624 and
a redis server on localhost port 6379. It runs a web server on port 8000,
so connecting with a browser to http://localhost:8000 
should enable you to view and control the connected instruments.
"""

version = "0.0.1"

if __name__ == "__main__":

    # any wsgi web server can serve the wsgi application produced by
    # indiwsgi.make_wsgi_app, in this example the web server 'waitress' is used

    from waitress import serve

    args = sys.argv

    if len(args) == 2:
        if args[1] == "--version":
            print(version)
            sys.exit(0)
        if (args[1] == "-h") or (args[1] == "--help"):
            print(DESCRIPTION)
            sys.exit(0)
        if args[1].startswith('-'):
            print("Unrecognised option. " + DESCRIPTION)
            sys.exit(1)
        blob_folder = os.path.abspath(os.path.expanduser(args[1]))
    else:
        print( "Invalid input. " + DESCRIPTION)
        sys.exit(2)


    # define the hosts/ports where servers are listenning, these functions return named tuples
    # which are required as arguments to inditoredis() and to indiwsgi.make_wsgi_app()

    indi_host = indi_server(host='localhost', port=7624)
    redis_host = redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_',
                              to_indi_channel='to_indi', from_indi_channel='from_indi')


    # create a wsgi application
    application = indiwsgi.make_wsgi_app(redis_host, blob_folder)
    if application is None:
        print("Are you sure the skipole framework is installed?")
        sys.exit(3)

    # add skiadmin during development, and run serve in this thread
    #application = indiwsgi.add_skiadmin(application)
    #serve(application, host = "127.0.0.1", port=8000)

    # comment out lines below during development

    # serve the application with the python waitress web server
    webapp = threading.Thread(target=serve, args=(application,), kwargs={'host':'127.0.0.1', 'port':8000})
    # and start it
    webapp.start()

    # and start inditoredis
    inditoredis(indi_host, redis_host, log_lengths={}, blob_folder=blob_folder)

