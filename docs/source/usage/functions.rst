The indiredis package
=====================

.. automodule:: indiredis

Functions in indiredis
^^^^^^^^^^^^^^^^^^^^^^

These first three functions are used to create named tuples gathering the data for the
associated servers.

.. autofunction:: indiredis.indi_server

.. autofunction:: indiredis.redis_server

.. autofunction:: indiredis.mqtt_server

The tuples created by the above functions are then used as parameters for the following functions.

.. autofunction:: indiredis.inditoredis

For further information on the log_lengths parameter see :ref:`log_lengths`.

So a minimal script using defaults to run inditoredis could be::

    from indiredis import inditoredis, indi_server, redis_server

    # define the hosts/ports where servers are listenning, these functions return named tuples
    # which are required as arguments to inditoredis().

    indi_host = indi_server(host='localhost', port=7624)
    redis_host = redis_server(host='localhost', port=6379)

    # blocking call which runs the service, communicating between indiserver and redis

    inditoredis(indi_host, redis_host, blob_folder='/path/to/blob_folder')

    # Set the blob_folder to a directory of your choice

The two functions below work together to provide communications via an MQTT server.

.. autofunction:: indiredis.inditomqtt

.. autofunction:: indiredis.mqtttoredis

.. _web_client:

indiwsgi
^^^^^^^^
.. automodule:: indiredis.indiwsgi

This module requires Python3 packages skipole and redis, available from Pypi.

The function which creates the wsgi application:

.. autofunction:: indiredis.indiwsgi.make_wsgi_app

This particular client application is general purpose, and learns all instrument properties from the
redis store, it employs a browser client refresh every ten seconds, and so may not be useful for an
instrument that updates data at a faster rate.

If this wsgi application is not used, the skipole package is not required by indiredis, and does not
have to be installed on your machine.

To run the application, the following is suggested which uses the waitress web server, therefore you
will also need waitress installing, again available from Pypi.

Assuming you have all the dependencies loaded, including a redis server and indiserver operating on
your localhost, you can use::

    python3 -m indiredis path/to/blobfolder

This runs the script __main__.py within indiredis, and serves the client at localhost:8000

If you want to import indiwsgi and run your own web server in your own script, further examples are
given below which can be adapted to your own system.

Open three terminals.

In terminal one, run indiserver with the simulated instruments::

    indiserver -v indi_simulator_telescope indi_simulator_dome indi_simulator_guide

In terminal two, run inditoredis using the minimal script described above.

In terminal three, run the following web service::

    import sys
    from indiredis import redis_server, indiwsgi

    # any wsgi web server can serve the wsgi application produced by
    # indiwsgi.make_wsgi_app, in this example the web server 'waitress' is used

    from waitress import serve

    redis_host = redis_server(host='localhost', port=6379)

    # create a wsgi application, which requires the redis_host tuple and
    # set the blob_folder to a directory of your choice
    application = indiwsgi.make_wsgi_app(redis_host, blob_folder='/path/to/blob_folder')
    if application is None:
        print("Are you sure the skipole framework is installed?")
        sys.exit(1)

    # blocking call which serves the application with the python waitress web server
    serve(application, host=127.0.0.1, port=8000)

Then, from your web browser connect to localhost:8000

Wait a few seconds, and the devices, with their properties, should be discovered and displayed.

To end the program, press Ctrl-c a few times in the terminal.

A further example, showing how inditoredis and the wsgi application with web server
can be run in separate threads from a single script::


    import threading, os, sys

    from indiredis import inditoredis, indi_server, redis_server, indiwsgi

    # any wsgi web server can serve the wsgi application produced by
    # indiwsgi.make_wsgi_app, in this example the web server 'waitress' is used

    from waitress import serve

    # define the hosts/ports where servers are listenning, these functions return named tuples
    # which are required as arguments to inditoredis() and to indiwsgi.make_wsgi_app()

    indi_host = indi_server(host='localhost', port=7624)
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

    # and start inditoredis
    inditoredis(indi_host, redis_host, blob_folder=BLOBS)


You will still need indiserver to be running first - either started in another terminal, or as a service. On
running this script in a terminal, connect your browser to localhost:8000 to view the web pages.

The __main__.py script in the indiredis package is very similar to the above example with the addition of
accepting the blob_folder as a script argument. 








