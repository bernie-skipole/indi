The indiredis package
=====================

.. automodule:: indiredis

Functions in indiredis
^^^^^^^^^^^^^^^^^^^^^^

These first three functions are used to create named tuples.

For example::

    from indiredis import indi_server, redis_server, mqtt_server

    indi_host = indi_server(host='localhost', port=7624)
    redis_host = redis_server(host='localhost', port=6379)
    mqtt_host = mqtt_server(host='localhost', port=1883)

These variables 'indi_host', 'redis_host' and 'mqtt_host' are then used as inputs to further functions which require definitions of the hosts.

.. autofunction:: indiredis.indi_server

.. autofunction:: indiredis.redis_server

.. autofunction:: indiredis.mqtt_server


The to_indi_topic should be a string, the same string should be used for every connection, so, for example, clients will send data
with this topic, and servers/drivers will subscribe to the topic to receive that data.

Similarly the from_indi_topic should be another, different string, again used for every connection.

The same rule follows for the snoop_control_topic and snoop_data_topic.

The tuples created by the above functions are then used as parameters for the following functions.

.. _inditoredis:

indiredis.inditoredis
^^^^^^^^^^^^^^^^^^^^^

An INDI client which reads data from indiserver (port 7624) converts the XML to redis key-value storage. In the other direction,
subscribes to XML data published via Redis and transmits to indiserver. Enables a GUI or web client to communicate to indiserver
purely via redis.

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

Note that BLOB's - Binary Large Objects, such as images are not stored in redis, but are set into a directory of your choice defined by the blob_folder argument.


.. _driverstoredis:

indiredis.driverstoredis
^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: indiredis.driverstoredis

A minimal script using defaults to run driverstoredis could be::

    from indiredis import driverstoredis, redis_server

    redis_host = redis_server(host='localhost', port=6379)

    # blocking call which runs the service, communicating between the drivers and redis

    driverstoredis(["indi_simulator_telescope", "indi_simulator_ccd"], redis_host, blob_folder='/path/to/blob_folder')

    # The list of two simulated drivers shown above should be replaced by a list of your own drivers.


As an alternative to inditoredis or driverstoredis, the functions below provide communications via an MQTT server.

.. _inditomqtt:

indiredis.inditomqtt
^^^^^^^^^^^^^^^^^^^^

Intended to be run on a device with indiserver, appropriate drivers and attached instruments.

Receives/transmitts XML data between indiserver on port 7624 and an MQTT server which ultimately sends data to the remote web/gui server.

.. autofunction:: indiredis.inditomqtt

Example Python script running on the machine with indiserver and the connected instruments::

    from indiredis import inditomqtt, indi_server, mqtt_server

    # define the hosts/ports where servers are listenning, these functions return named tuples.

    indi_host = indi_server(host='localhost', port=7624)
    mqtt_host = mqtt_server(host='10.34.167.1', port=1883)

    # blocking call which runs the service, communicating between indiserver and mqtt

    inditomqtt(indi_host, 'indi_server01', mqtt_host)

Substitute your own MQTT server ip address for 10.34.167.1, and your own mqtt id for 'indi_server01'.

To be specific, the mqtt_id should be unique for every connection to the MQTT network.

When choosing an mqtt_id, consider using a prefix, to avoid clashing with other users of the MQTT broker,
such as indi_server01, or indi_client01.

.. _driverstomqtt:

indiredis.driverstomqtt
^^^^^^^^^^^^^^^^^^^^^^^

Connects INDI drivers and attached instruments to the MQTT network without needing indiserver.

.. autofunction:: indiredis.driverstomqtt

Example Python script running on the machine with the connected instruments::

    from indiredis import driverstomqtt, mqtt_server

    # define the host/port where the MQTT server is listenning, this function returns a named tuple.

    mqtt_host = mqtt_server(host='10.34.167.1', port=1883)

    # blocking call which runs the service, communicating between drivers and mqtt

    driverstomqtt(["indi_simulator_telescope", "indi_simulator_ccd"], 'indi_drivers01', mqtt_host)

    # The list of two simulated drivers shown above should be replaced by a list of your own drivers.

Substitute your own MQTT server ip address for 10.34.167.1, and your own mqtt id for 'indi_drivers01'.

.. _mqtttoredis:

indiredis.mqtttoredis
^^^^^^^^^^^^^^^^^^^^^

Intended to be run on the same server running a redis service, typically with the gui or web service which can read/write to redis.

An INDI client which receives XML data from the MQTT server and converts to redis key-value storage, and reads data published to redis, and sends to the MQTT server.

.. autofunction:: indiredis.mqtttoredis

Example Python script running at the redis server::

    from indiredis import mqtttoredis, mqtt_server, redis_server

    # define the hosts/ports where servers are listenning, these functions return named tuples.

    mqtt_host = mqtt_server(host='10.34.167.1', port=1883)
    redis_host = redis_server(host='localhost', port=6379)

    # blocking call which runs the service, communicating between mqtt and redis

    mqtttoredis('indi_client01', mqtt_host, redis_host, blob_folder='/path/to/blob_folder')


Set the blob_folder to a directory of your choice and substitute your own MQTT server ip address for 10.34.167.1, and mqtt id for 'indi_client01'.

.. _mqtttoport:

indiredis.mqtttoport
^^^^^^^^^^^^^^^^^^^^^

Transfers XML data between the MQTT server and a server port, which can connect to a traditional INDI client.

.. autofunction:: indiredis.mqtttoport

Example Python script::

    from indiredis import mqtttoport, mqtt_server

    # define the mqtt server

    mqtt_host = mqtt_server(host='10.34.167.1', port=1883)

    # blocking call which runs the service, communicating between mqtt and the port

    mqtttoport("indi_port01", mqtt_host, port=7624)


Substitute your own MQTT server ip address for 10.34.167.1, and mqtt id for 'indi_port01'.

.. _web_client:

indiwsgi
^^^^^^^^
.. automodule:: indiredis.indiwsgi

This module requires Python3 packages skipole and redis, available from Pypi.

The function which creates the wsgi application:

.. autofunction:: indiredis.indiwsgi.make_wsgi_app

This particular client application is general purpose, learning all instrument properties from the
redis store.

If this wsgi application is not used, the skipole package is not required by indiredis, and does not
have to be installed on your machine.

To run the application, the following is suggested which uses the waitress web server, therefore you
will also need waitress installing, again available from Pypi.

Assuming you have all the dependencies loaded, including a redis server and indiserver operating on
your localhost, you can use::

    python3 -m indiredis path/to/blobfolder

This runs the script __main__.py within indiredis, and serves the client at localhost:8000

You can also try::

    python3 -m indiredis -h

For help on the full set of arguments available.

If you want to import indiwsgi and run your own web server in your own script, further examples are
given below which can be adapted to your own system.

Open three terminals.

In terminal one, run indiserver with the simulated instruments::

    indiserver -v indi_simulator_telescope indi_simulator_ccd

In terminal two, run inditoredis with the following script::

    from indiredis import inditoredis, indi_server, redis_server

    indi_host = indi_server(host='localhost', port=7624)
    redis_host = redis_server(host='localhost', port=6379)

    inditoredis(indi_host, redis_host, blob_folder='/path/to/blob_folder')

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

A further example, still with indiserver running in another terminal, which shows how inditoredis
and the web service can be run by a single script::

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


On running this script in a terminal, connect your browser to localhost:8000 to view the web pages.

The __main__.py script in the indiredis package is very similar to the above example with the addition of
accepting host, port, blob_folder, etc., as script arguments.

And a further example using the driverstoredis function, which does not need indiserver::

    import threading, os, sys

    from indiredis import driverstoredis, redis_server, indiwsgi

    # any wsgi web server can serve the wsgi application produced by
    # indiwsgi.make_wsgi_app, in this example the web server 'waitress' is used

    from waitress import serve

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






