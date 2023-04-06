The indiredis package
=====================

.. automodule:: indiredis




Command line
^^^^^^^^^^^^

This particular client application is general purpose, learning all instrument properties from the
redis store.

Assuming you have all the dependencies loaded, including a redis server and indiserver operating on
your localhost, you can use::

    python3 -m indiredis path/to/blobfolder

This runs the script __main__.py within indiredis, and serves the client at localhost:8000

You can also try::

    python3 -m indiredis --help

which displays::

    usage: python3 -m indiredis [options] blobdirectorypath

    INDI web client communicating to indiserver and saving data to redis and to a
    BLOB directory.

    positional arguments:
      blobdirectorypath     Path of the directory where BLOB's will be set

    optional arguments:
      -h, --help            show this help message and exit
      -p PORT, --port PORT  Port of the web service (default 8000).
      --host HOST           Listenning IP address of the web service (default localhost).
      --iport IPORT         Port of the indiserver (default 7624).
      --ihost IHOST         Hostname of the indiserver (default localhost).
      --rport RPORT         Port of the redis server (default 6379).
      --rhost RHOST         Hostname of the redis server (default localhost).
      --prefix PREFIX       Prefix applied to redis keys (default indi_).
      --toindipub TOINDIPUB
                            Redis channel used to publish data to indiserver
                            (default to_indi).
      --fromindipub FROMINDIPUB
                            Redis channel on which data is published from
                            indiserver (default from_indi).
      --version             show program's version number and exit


Apart from the command line, indiredis can be imported which makes the following functions available.


runclient
^^^^^^^^^

.. autofunction:: indiredis.runclient


This can be used in your own python script, for example::

    import indiredis

    # blocking call
    indiredis.runclient("/path/to/configfile")

and this would run the web client.

The configfile must exist, and should have format::

    [WEB]
    # Set this to the folder where Blobs will be stored
    blob_folder = path/to/blob/folder
    # Set this to a hashed password string which will be required to access the
    # web pages, or do not include this parameter if no password is required
    hashedpassword = hash-of-password
    # web service host and port
    host = localhost
    port = 8000

    # only one of the following [INDI], [MQTT] or [DRIVERS] should
    # be given. They are mutually exclusive.

    [INDI]
    # indi server host and port
    ihost = localhost
    iport = 7624

    # [MQTT]
    # mqtt server host, port and client id
    # mhost = localhost
    # mport = 1883
    # mqtt_id = indi_client01

    # [DRIVERS]
    # a list of drivers, for example
    # indi_simulator_telescope
    # indi_simulator_ccd

    [REDIS]
    # redis server host and port
    rhost = localhost
    rport = 6379
    # Prefix applied to redis keys
    prefix = indi_
    # Redis channel used to publish data to indiserver
    toindipub = to_indi
    # Redis channel on which data is published from indiserver
    fromindipub = from_indi

It should be noted this has a web client password option. If not included, no password is applied, however if set as::

    hashedpassword = hashstring

Where the string is the hash of a password, then the web site will show a login page, and will require the password to be submitted.

The hash can be created using::

    import hashlib
    password = "mypassword"
    print(hashlib.sha512( password.encode('utf-8') ).hexdigest())

And the result copied to the config file. This has the advantage that no password is stored in clear on the server.

As well as creating the config file manually, you could use the following function.


confighelper
^^^^^^^^^^^^

.. autofunction:: indiredis.confighelper


Typically, in the REPL you would run::

    import indiredis
    indiredis.confighelper("/path/to/new/configfile")

You will be asked for each parameter, this function will do the password hashing, and will finally produce the config file.

Using a config file to provide parameters may be usefull where docker containers are used, as config files in a drive
shared with a host can be easily changed, as opposed to creating new containers. The runclient function parses the config
file and then calls further functions - these are also available if you want to create your own scripts, and are described
below.


make_wsgi_app
^^^^^^^^^^^^^

.. autofunction:: indiredis.make_wsgi_app


make_wsgi_app can be used if you want to run your own WSGI web server in your own script, further examples are
given below which can be adapted to your own system.

For example, open three terminals.

In terminal one, run indiserver with the simulated instruments::

    indiserver -v indi_simulator_telescope indi_simulator_ccd

In terminal two, run inditoredis with the following script::

    from indi_mr import inditoredis, indi_server, redis_server

    indi_host = indi_server(host='localhost', port=7624)
    redis_host = redis_server(host='localhost', port=6379)

    inditoredis(indi_host, redis_host, blob_folder='/path/to/blob_folder')

In terminal three, run the following web service::

    from indi_mr import redis_server
    from indiredis import make_wsgi_app

    # any wsgi web server can serve the wsgi application produced by
    # make_wsgi_app, in this example the web server 'waitress' is used

    from waitress import serve

    redis_host = redis_server(host='localhost', port=6379)

    # create a wsgi application, which requires the redis_host tuple and
    # set the blob_folder to a directory of your choice
    application = make_wsgi_app(redis_host, blob_folder='/path/to/blob_folder')

    # blocking call which serves the application with the python waitress web server
    serve(application, host="localhost", port=8000)

Then, from your web browser connect to localhost:8000

Wait a few seconds, and the devices, with their properties, should be discovered and displayed.

To end the program, press Ctrl-c a few times in the terminal.

For further information on the functions provided by indi_mr, see the documentation at:

https://indi-mr.readthedocs.io

A further example, still with indiserver running in another terminal, which shows how inditoredis
and the web service can be run by a single script::

    import threading

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

    import threading

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

    # serve the application with the python waitress web server in its own thread
    webapp = threading.Thread(target=serve, args=(application,), kwargs={'host':'localhost', 'port':8000})
    # and start it
    webapp.start()

    # and start driverstoredis
    driverstoredis(["indi_simulator_telescope", "indi_simulator_ccd"], redis_host, blob_folder=BLOBS)


INDI over MQTT
^^^^^^^^^^^^^^

The project indi-mr includes functions for transmitting INDI data via an MQTT broker. For complete information
see the indi-mr documentation. The example below shows how it could be used with the indiredis client.

If these scripts are to be used, your machines need the Python MQTT client which is used by the indi-mr
functions. This requires:

python3 -m pip install paho-mqtt

At the remote sites where instruments and drivers are connected, the following script is run::

    from indi_mr import driverstomqtt, mqtt_server

    # define the host/port where the MQTT server is listenning, this function returns a named tuple.

    mqtt_host = mqtt_server(host='10.34.167.1', port=1883)

    # blocking call which runs the service, communicating between drivers and mqtt

    driverstomqtt(["indi_simulator_telescope", "indi_simulator_ccd"], 'indi_drivers01', mqtt_host)

    # The list of two simulated drivers shown above should be replaced by a list of your own drivers.

Substitute your own MQTT server ip address for 10.34.167.1, and a unique mqtt id for 'indi_drivers01',
if you have another set of drivers connecting to the MQTT server, possibly from a different location,
then they should use a different mqtt id.

The above script uses the blocking function driverstomqtt to run the drivers, and publishes/receives
INDI data via MQTT. At the central site where the redis and web servers are, you could simply call
the indiredis.runclient function, with the config file specifying the MQTT parameters.

Alternatively you could run a script such as::


    import threading

    from indi_mr import mqtttoredis, mqtt_server, redis_server

    from indiredis import make_wsgi_app

    # any wsgi web server can serve the wsgi application produced by
    # make_wsgi_app, in this example the web server 'waitress' is used

    from waitress import serve

    mqtt_host = mqtt_server(host='10.34.167.1', port=1883)
    redis_host = redis_server(host='localhost', port=6379)

    # Set a directory of your choice where blobs will be stored
    BLOBS = '/path/to/blob_folder'

    # create a wsgi application
    application = make_wsgi_app(redis_host, blob_folder=BLOBS)

    # serve the application with the python waitress web server in its own thread
    webapp = threading.Thread(target=serve, args=(application,), kwargs={'host':'localhost', 'port':8000})
    # and start it
    webapp.start()

    # and start mqtttoredis
    mqtttoredis('indi_client01', mqtt_host, redis_host, blob_folder=BLOBS)


The blocking function mqtttoredis converts the INDI data received via MQTT to redis stored data, which is
served by the indiredis client running in its own thread. Again this server would need the indi-mr and the
paho-mqtt packages installing.

The indi-mr package provides the function mqtttoredis, note it has further arguments subscribe_list
and log_lengths which may be usefull, refer to the indi-mr documentation for details.


Web client limitation
^^^^^^^^^^^^^^^^^^^^^

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
and add .gz to the extension format, and will then send the data on to the remote INDI drivers.

Note: this is done by holding the file in variables (in memory) rather than reading/writing to disc, which
may not work with very large files.

This package, and indi-mr, is the work of a single developer. In the situation where connections are made
across a network the multiple scenarios of possible network failures are difficult to handle. For the most
stable outcome, run everything on a single machine.

Do not use this::

    To control a nuclear power station
    To control a strategic missile defence system
    To control anything remotely critical
