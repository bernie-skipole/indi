Introduction
============

Python INDI client package. With option of MQTT transmission.

INDI - Instrument Neutral Distributed Interface, see https://en.wikipedia.org/wiki/Instrument_Neutral_Distributed_Interface

Though INDI is used for astronomical instruments, it can also be used for any instrument control if appropriate INDI drivers are available.

This project provides a client, not drivers, nor indiserver. It is assumed that indiserver is installed and running, together with appropriate drivers and connected instruments.

See https://indilib.org/ for these components.

This Python3 package provides an INDI client with the capability to read instrument properties from indiserver (port 7624) and store them in redis, and in the
other direction; can read data published to redis and send it in INDI XML format to indiserver.

This is done to provide a web framework (or other gui) easy access to device properties and settings via redis key value storage. An example web service is provided. As the code for this project is developed, the redis keys will be defined and documented here.

indiredis code is developed at https://github.com/bernie-skipole/indi

Two options are provided :

The data can be parsed and transferred between indiserver and redis.

or

The data can be transferred between indiserver and redis via an MQTT server.

Python dependencies: The python3 "redis" client, and, if the MQTT option is required, "paho-mqtt".

If the example web service is to be run, skipole (wsgi generator) and waitress (web server) are needed:

For debian systems

sudo apt-get install python3-pip

sudo -H pip3 install skipole

sudo -H pip3 install waitress

sudo -H pip3 install redis

sudo -H pip3 install paho-mqtt


Server dependencies: A redis server (apt-get install redis-server), and, if the MQTT option is used, an MQTT server (apt-get install mosquitto)

The indiredis package provides functions which can be used by your own script:

indiredis.inditoredis
^^^^^^^^^^^^^^^^^^^^^

Converts directly between indiserver (port 7624) and redis, converting indi XML to redis key-value storage.

For example, your Python script to import and run this service could be::

    from indiredis import inditoredis, indi_server, redis_server

    # define the hosts/ports where servers are listenning, these functions return named tuples
    # which are required as arguments to inditoredis().

    indi_host = indi_server(host='localhost', port=7624)
    redis_host = redis_server(host='localhost', port=6379)

    # blocking call which runs the service, communicating between indiserver and redis

    inditoredis(indi_host, redis_host)

indiredis.indiwsgi
^^^^^^^^^^^^^^^^^^

Your own web framework could be used to write code that can read and write to a redis service. However the package indiredis.indiwsgi is provided which creates a Python WSGI application that can provide a demonstration web service. It displays connected devices and properties, and allows the user to set properties according to the Indi specification.

WSGI - https://wsgi.readthedocs.io/en/latest/what.html

WSGI is a specification that describes how a web server communicates with web applications. indiwsgi is such an application, and produces html and javascript code which is then served by a web server that understands wsgi.

indiwsgi requires the 'skipole' Python framework, available from Pypi, and a wsgi web server, such as 'waitress' also available from Pypi.

An example of creating the wsgi application, and running it with waitress is given at :ref:`web_client`.

As an alternative to the inditoredis function, two further functions are provided, inditomqtt and mqtttoredis, these work together to transfer the xml data from the indiserver port 7624 to an mqtt server, and from the mqtt server to redis, where again indiwsgi could be used to create a web service.


indiredis.inditomqtt
^^^^^^^^^^^^^^^^^^^^

Intended to be run on a device with indiserver, appropriate drivers and attached instruments.

Receives/transmitts XML data between indiserver on port 7624 and an MQTT server which ultimately sends data to the remote web/gui server.

Example Python script running on the machine with the connected instruments::

    from indiredis import inditomqtt, indi_server, mqtt_server

    # define the hosts/ports where servers are listenning, these functions return named tuples.

    indi_host = indi_server(host='localhost', port=7624)
    mqtt_host = mqtt_server(host='10.34.167.1', port=1883)

    # blocking call which runs the service, communicating between indiserver and mqtt

    inditomqtt(indi_host, mqtt_host)

Substitute your own MQTT server ip address for 10.34.167.1 in the above example.

indiredis.mqtttoredis
^^^^^^^^^^^^^^^^^^^^^

Intended to be run on the same server running a redis service, typically with the gui or web service which can read/write to redis.

Receives XML data from the MQTT server and converts to redis key-value storage, and reads data published to redis, and sends to the MQTT server.

Example Python script running at the redis server::

    from indiredis import mqtttoredis, mqtt_server, redis_server

    # define the hosts/ports where servers are listenning, these functions return named tuples.

    mqtt_host = mqtt_server(host='10.34.167.1', port=1883)
    redis_host = redis_server(host='localhost', port=6379)

    # blocking call which runs the service, communicating between mqtt and redis

    mqtttoredis(mqtt_host, redis_host)

Substitute your own MQTT server ip address for 10.34.167.1 in the above example.

indiredis.tools
^^^^^^^^^^^^^^^
The tools module contains a set of Python functions, which your gui may use if convenient. These read the indi devices and properties from redis, returning Python lists and dictionaries, and provides functions to transmit indi commands by publishing to redis.

redis - why?
^^^^^^^^^^^^

redis is used as:

More than one web process or thread may be running, redis makes data visible to all processes.

As well as simply storing values for other processes to read, redis has a pub/sub functionality. When data is received, indiredis stores it, and publishes a notification on the from_indi_channel, which can alert a subscribing GUI application that a value has changed.

When the gui wishes to send data, it can publish it on the to_indi_channel, where it will be picked up by this indiredis service, and sent to indiserver.

Redis key/value storage and publication is extremely easy, most web frameworks already use it.

mqtt - why?
^^^^^^^^^^^

MQTT is an option provided here since it makes out-of-band communications easy, for example, if other none-INDI communications are needed between devices, then merely subscribing and publishing with another topic is possible.

There is flexibility in where the MQTT server is sited, it could run on the web server, or on a different machine entirely. This makes it possible to choose the direction of the initial connection - which may be useful when passing through NAT firewalls.

As devices connect to the MQTT server, only the IP address of the MQTT server needs to be fixed, a device running indiserver could, for instance, have a dynamic DHCP served address, and a remote GUI could also have a dynamic address, but since both initiate the call to the MQTT server, this does not matter.

It allows monitoring of the communications by a third device or service by simply subscribing to the topic used. This makes a possible logging service easy to implement.

A disadvantage may be a loss of throughput and response times. An extra layer of communications plus networking is involved, so this may not be suitable for all scenarios.

Security
^^^^^^^^

Only open communications is defined in this package, security and authentication is not considered. Transmission between servers could pass over an encrypted VPN or SSH tunnel. Any such implementation is not described here.

The web service provided here does not apply any authentication.


