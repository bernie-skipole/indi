

"""Example script to run inditoredis and the indiweb web service"""

import threading, os, sys


############ these lines for development mode ###########
skipole_package_location = "/home/bernard/git/skipole"

if skipole_package_location not in sys.path:
    sys.path.insert(0,skipole_package_location)
##########################################################

####### indiserver should be running in a separate process, for example, in another terminal, run:
####### indiserver -v indi_simulator_telescope indi_simulator_dome indi_simulator_guide


from indiredis import inditoredis, indi_server, redis_server, indiweb

# any wsgi web server can serve the wsgi application produced by
# indiweb.make_wsgi_app, in this example the web server 'waitress' is used

from waitress import serve


# define the hosts/ports where servers are listenning, these functions return named tuples
# which are required as arguments to inditoredis() and to indiweb.make_wsgi_app()

indi_host = indi_server(host='localhost', port=7624)
redis_host = redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_',
                          to_indi_channel='to_indi', from_indi_channel='from_indi')


# call inditoredis - which is blocking, so run in its own thread
run_inditoredis = threading.Thread(target=inditoredis, args=(indi_host, redis_host))
# and start it
run_inditoredis.start()

# create a wsgi application, which requires the redis_host tuple
application = indiweb.make_wsgi_app(redis_host)

# add skiadmin during development
# application = indiweb.add_skiadmin(application)

# serve the application with the python waitress web server
serve(application, host='127.0.0.1', port=8000)


