Introduction
============


The indiredis package
^^^^^^^^^^^^^^^^^^^^^

This Python3 package provides an INDI client with the capability to read instrument properties from indiserver (port 7624) and store them in redis, and in the
other direction; can read data published to redis and send it in INDI XML format to indiserver. If the package is run, this provides instrument control via a web service. If imported, it provides tools to read/write to redis, and hence indiserver, for use by your own GUI or WEB applications.

The package is a client only, it does not include indiserver or drivers.

INDI - Instrument Neutral Distributed Interface, see https://en.wikipedia.org/wiki/Instrument_Neutral_Distributed_Interface

Though INDI is used for astronomical instruments, it can also be used for any instrument control if appropriate INDI drivers are available.

Your host should have a redis server running, and indiserver should also be running, together with appropriate drivers and connected instruments. For example, prior to running indiredis, in another terminal, run::

    indiserver -v indi_simulator_telescope indi_simulator_ccd

Usage is then::

    python3 -m indiredis /path/to/blobfolder


The directory /path/to/blobfolder should be a path to a directory of your choice, where BLOB's (Binary Large Objects), such as images are stored, it will be created if it does not exist. Then connecting with a browser to http://localhost:8000 should enable you to view and control the connected instruments.

For further usage information, including setting ports and hosts, try::

    python3 -m indiredis --help


Dependencies
^^^^^^^^^^^^

Server dependencies: A redis server (For debian systems; apt-get install redis-server), and indiserver (apt-get install indi-bin).

For debian systems you may need apt-get install python3-pip, and then use whichever variation of the pip command required by your environment, one example being:

sudo -H pip3 install indiredis

The file requirements.txt lists the Python packages required which are available via pip, so as well as indiredis, the above command should pull in the packages: 

skipole - required for the built in web service, not needed if you are making your own GUI

waitress - Python web server, not needed if you are creating your own gui, or using a different web server.

redis - Python redis client, needed.

indiredis also features functions for transferring data between indiserver and redis via an MQTT server. If these are used, then an MQTT server (apt-get install mosquitto) is needed, and also:

paho-mqtt - Python MQTT client, also available via pip, and listed in requirements.txt


Importing indiredis
^^^^^^^^^^^^^^^^^^^

indiredis can be imported into your own scripts, rather than executed with python3 -m. This is particularly aimed at helping the developer create their own GUI's or controlling scripts, perhaps more specialised than the web client included.

Two options are available:

The data can be transferred between indiserver and redis.

or

The data can be transferred between indiserver and redis via an MQTT server.

The indiredis package provides the following which can be used by your own script:

**indiredis.inditoredis()**

The primary function of the package which converts between indiserver and redis, providing redis key-value storage of the instrument parameters, and works with the pub/sub faciliies of redis.

For an example of usage, see :ref:`inditoredis`.

**indiredis.indiwsgi.make_wsgi_app()**

The package indiredis.indiwsgi is provided with the function make_wsgi_app which creates a Python WSGI application that provides the included web client.

WSGI is a specification that describes how a web server communicates with web applications. The function make_wsgi_app creates such an application, and produces html and javascript code which can then be served by any WSGI compatable web server. When indiredis is executed, the __main__.py module is run, which imports and uses the waitress web server to serve the application. It is possible to use a different WSGI-compatable web server to run the application in your own script if desired.  

An example of creating the wsgi application, and running it with waitress is given at :ref:`web_client`.

As an alternative to the inditoredis function, two further functions are provided, inditomqtt and mqtttoredis, these work together to transfer the xml data from indiserver to an mqtt server, and from the mqtt server to redis, where again indiwsgi could be used to create a web service, or your own application could interface to redis.

**indiredis.inditomqtt()**

Intended to be run on a device with indiserver, appropriate drivers and attached instruments.

Receives/transmitts XML data between indiserver and an MQTT server which ultimately sends data to the remote web/gui server.

For an example of usage, see :ref:`inditomqtt`.


**indiredis.mqtttoredis()**

Receives XML data from the MQTT server and converts to redis key-value storage, and reads data published to redis, and sends to the MQTT server.

For an example of usage, see :ref:`mqtttoredis`.


**indiredis.tools**

The tools module contains a set of Python functions, which your gui may use if convenient. These read the indi devices and properties from redis, returning Python lists and dictionaries, and provides functions to transmit indi commands by publishing to redis.

The tools functions are described at :ref:`tools`.

redis - why?
^^^^^^^^^^^^

redis is used as:

More than one web process or thread may be running, redis makes data from a single connection visible to all processes.

As well as simply storing values for other processes to read, redis has a pub/sub functionality. When data is received, indiredis stores it, and publishes the XML data on the from_indi_channel, which could be used to alert a subscribing GUI application that a value has changed.

When the gui wishes to send data, it can publish it on the to_indi_channel, where it will be picked up by this indiredis service, and sent to indiserver.

Redis key/value storage and publication is extremely easy, many web frameworks already use it.

mqtt - why?
^^^^^^^^^^^

MQTT is an option provided here since it makes out-of-band communications easy, for example, if other none-INDI communications are needed between devices, then merely subscribing and publishing with another topic is possible.

There is flexibility in where the MQTT server is sited, it could run on the web server, or on a different machine entirely. This makes it possible to choose the direction of the initial connection - which may be useful when passing through NAT firewalls.

As devices connect to the MQTT server, only the IP address of the MQTT server needs to be fixed, a device running indiserver could, for instance, have a dynamic DHCP served address, and a remote GUI could also have a dynamic address, but since both initiate the call to the MQTT server, this does not matter.

It allows monitoring of the communications by a third device or service by simply subscribing to the topic used. This makes a possible logging service easy to implement.

A disadvantage may be a loss of throughput and response times. An extra layer of communications plus networking is involved, so this may not be suitable for all scenarios.

Security
^^^^^^^^

Only open communications are defined in this package, security and authentication are not considered.

The web service provided here does not apply any authentication.


