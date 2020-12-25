The indiredis package
=====================

.. automodule:: indiredis

make_wsgi_app
^^^^^^^^^^^^^

.. autofunction:: indiredis.make_wsgi_app


This particular client application is general purpose, learning all instrument properties from the
redis store.

Assuming you have all the dependencies loaded, including a redis server and indiserver operating on
your localhost, you can use::

    python3 -m indiredis path/to/blobfolder

This runs the script __main__.py within indiredis, and serves the client at localhost:8000

You can also try::

    python3 -m indiredis -h

For help on the full set of arguments available.

If you want to import indiredis and run your own web server in your own script, further examples are
given below which can be adapted to your own system.

Open three terminals.

In terminal one, run indiserver with the simulated instruments::

    indiserver -v indi_simulator_telescope indi_simulator_ccd

In terminal two, run inditoredis with the following script::

    from indi_mr import inditoredis, indi_server, redis_server

    indi_host = indi_server(host='localhost', port=7624)
    redis_host = redis_server(host='localhost', port=6379)

    inditoredis(indi_host, redis_host, blob_folder='/path/to/blob_folder')

In terminal three, run the following web service::

    import sys
    from indi_mr import redis_server
    from indiredis import make_wsgi_app

    # any wsgi web server can serve the wsgi application produced by
    # make_wsgi_app, in this example the web server 'waitress' is used

    from waitress import serve

    redis_host = redis_server(host='localhost', port=6379)

    # create a wsgi application, which requires the redis_host tuple and
    # set the blob_folder to a directory of your choice
    application = make_wsgi_app(redis_host, blob_folder='/path/to/blob_folder')
    if application is None:
        print("ERROR: Are you sure the skipole framework is installed?")
        sys.exit(1)

    # blocking call which serves the application with the python waitress web server
    serve(application, host="localhost", port=8000)

Then, from your web browser connect to localhost:8000

Wait a few seconds, and the devices, with their properties, should be discovered and displayed.

To end the program, press Ctrl-c a few times in the terminal.

A further example, still with indiserver running in another terminal, which shows how inditoredis
and the web service can be run by a single script::

    import threading, os, sys

    from indi_mr import inditoredis, indi_server, redis_server

    from indiredis import make_wsgi_app

    # any wsgi web server can serve the wsgi application produced by
    # make_wsgi_app, in this example the web server 'waitress' is used

    from waitress import serve

    # define the hosts/ports where servers are listenning, these functions return named tuples
    # which are required as arguments to inditoredis() and to indiwsgi.make_wsgi_app()

    indi_host = indi_server(host='localhost', port=7624)
    redis_host = redis_server(host='localhost', port=6379)

    # Set a directory of your choice where blobs will be stored
    BLOBS = '/path/to/blob_folder'

    # create a wsgi application
    application = make_wsgi_app(redis_host, blob_folder=BLOBS)
    if application is None:
        print("ERROR:Are you sure the skipole framework is installed?")
        sys.exit(1)

    # serve the application with the python waitress web server in its own thread
    webapp = threading.Thread(target=serve, args=(application,), kwargs={'host':'localhost', 'port':8000})
    # and start it
    webapp.start()

    # and start inditoredis
    inditoredis(indi_host, redis_host, blob_folder=BLOBS)


On running this script in a terminal, connect your browser to localhost:8000 to view the web pages.

The __main__.py script in the indiredis package is very similar to the above example with the addition of
accepting host, port, blob_folder, etc., as script arguments.

And a further example using the driverstoredis function, which does not need indiserver::

    import threading, os, sys

    from indi_mr import driverstoredis, redis_server

    from indiredis import make_wsgi_app

    # any wsgi web server can serve the wsgi application produced by
    # make_wsgi_app, in this example the web server 'waitress' is used

    from waitress import serve

    redis_host = redis_server(host='localhost', port=6379)

    # Set a directory of your choice where blobs will be stored
    BLOBS = '/path/to/blob_folder'

    # create a wsgi application
    application = make_wsgi_app(redis_host, blob_folder=BLOBS)
    if application is None:
        print("ERROR:Are you sure the skipole framework is installed?")
        sys.exit(1)

    # serve the application with the python waitress web server in its own thread
    webapp = threading.Thread(target=serve, args=(application,), kwargs={'host':'localhost', 'port':8000})
    # and start it
    webapp.start()

    # and start driverstoredis
    driverstoredis(["indi_simulator_telescope", "indi_simulator_ccd"], redis_host, blob_folder=BLOBS)


**Web client limitation**

The web client employs a browser refresh every ten seconds, so data changes which update at a faster rate
will jump rather than change smoothly.

Sending BLOB's from client to device is achieved on the browser by giving the user the option of uploading
a file. This may be required for certain instruments, which may, for example, need a configuration uploaded,
or a script of instructions.

The indi protocol requires the file format and the size before compression to be set in the XML data. This
wsgi application uses the uploaded filename extension as the format, and the uploaded file size as the 'size'
parameter. To comply with the specification therefore you should only upload uncompressed files.

The web client gives you the option to request file compression. If this is chosen, the wsgi application will
take your uploaded uncompressed file (from which it derives the size) and will then compress it using gzip,
and add .gz to the extension format, and will then send the data on to indiserver.

Note: this is done by holding the file in variables (in memory) rather than reading/writing to disc, which
may not work with very large files.






