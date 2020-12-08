# indiredis

This Python3 package provides an INDI client for general Instrument control, converting between the INDI protocol and redis storage. It also includes functions for transferring the INDI protocol via MQTT. If the package is run, it provides a web service for controlling instruments. If imported, it provides tools to read/write to redis and MQTT, and hence the INDI protocol, for use by your own Python applications.

INDI - Instrument Neutral Distributed Interface.

See https://en.wikipedia.org/wiki/Instrument_Neutral_Distributed_Interface

The package does not include indiserver or drivers, but is compatable with them.

Though INDI is generally used for astronomical instruments, it can work with any instrument if appropriate INDI drivers are available.

Your host should have a redis server running, typically with instruments connected by appropriate drivers and indiserver. For example, in one terminal, run:

> indiserver -v indi_simulator_telescope indi_simulator_ccd

Usage of this client is then:

> python3 -m indiredis /path/to/blobfolder


The directory /path/to/blobfolder should be a path to a directory of your choice, where BLOB's (Binary Large Objects), such as images will be stored, it will be created if it does not exist. Then connecting with a browser to http://localhost:8000 should enable you to view and control the connected instruments.

For further usage information, including setting ports and hosts, try:

> python3 -m indiredis --help


## Installation

Server dependencies: A redis server (For debian systems; apt-get install redis-server), and indiserver with drivers (apt-get install indi-bin). If you are using the MQTT functions you will also need an MQTT server on your network (apt-get install mosquitto). 

For debian systems you may need apt-get install python3-pip, and then use whichever variation of the pip command required by your environment, one example being:

> python3 -m pip install indiredis

Using a virtual environment may be preferred, if you need further information on pip and virtual environments, try:

https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

The above pip command should automatically pull in the following packages: 

skipole - required for the built in web service, not needed if you are making your own GUI client.

waitress - Python web server, not needed if you are creating your own gui, or using a different web server.

redis - Python redis client, needed.

paho-mqtt - Python MQTT client, only needed if you are using the MQTT facility.

If you do not want the python dependencies to be automatically installed with pip, then use the --no-deps option:

> python3 -m pip install --no-deps indiredis


## Importing indiredis

indiredis can be imported into your own scripts, rather than executed with python3 -m. This is particularly aimed at helping the developer create their own GUI's or controlling scripts, perhaps more specialised than the web client included.

The indiredis package provides the following which can be used by your own script:


**indiredis.inditoredis()**

The primary function of the package which converts between indiserver and redis, providing redis key-value storage of the instrument parameters, and works with the pub/sub facilities of redis.


**indiredis.driverstoredis()**

This function can take a list of drivers and will run them, without needing indiserver. Again it will provide redis key-value storage of the instrument parameters.


**indiredis.indiwsgi.make_wsgi_app()**

The package indiredis.indiwsgi provides the function make_wsgi_app which returns a Python WSGI application.

WSGI is a specification that describes how a web server communicates with web applications. The function make_wsgi_app creates such an application, and produces html and javascript code which can then be served by any WSGI compatable web server. When indiredis is executed with the python3 -m option, the waitress web server is imported to serve the application. It is possible to use a different WSGI-compatable web server in your own script if desired.

Further functions are provided to transfer INDI xml data via an mqtt server to redis, where again indiwsgi could be used to create a web service, or your own application could interface to redis.


**indiredis.inditomqtt()**

Intended to be run on a device with indiserver, appropriate drivers and attached instruments.

Receives/transmitts XML data between indiserver and an MQTT server which ultimately sends data to the remote web/gui client.


**indiredis.driverstomqtt()**

This function can take a list of drivers and will run them, without needing indiserver.

Receives/transmitts XML data between the drivers and an MQTT server which ultimately sends data to the remote web/gui client.


**indiredis.mqtttoredis()**

Receives XML data from the MQTT server and converts to redis key-value storage, and reads data published to redis, and sends to the MQTT server.


**indiredis.mqtttoport()**

Opens a server port. If a client is connected, forwards data from MQTT to the client, if data received from the client, passes it to MQTT.


**indiredis.tools**

The tools module contains a set of Python functions, which your own Python script may use if convenient. These read the indi devices and properties from redis, returning Python lists and dictionaries, and provides functions to transmit indi commands by publishing to redis.


## redis - why?

redis is used as:

A web application typically has more than one process or thread running, redis makes common data visible to all such processes.

As well as simply storing values for other processes to read, redis has a pub/sub functionality. When data is received, indiredis stores it, and publishes the XML data on the from_indi_channel, which could be used to alert a subscribing client application that a value has changed.

Redis key/value storage and publication is extremely easy, many web frameworks already use it.

## mqtt - why?

MQTT is an option providing distributed communications. In particular, scripts calling the driverstomqtt() function at different sites,
connected to distributed instruments, enables them to be controlled from a single client.

There is flexibility in where the MQTT server is sited, it could run on the web server, or on a different machine entirely. This makes it possible to choose the direction of the initial connection - which may be useful when passing through NAT firewalls.

As devices connect to the MQTT server, only the IP address of the MQTT server needs to be fixed, a remote device could, for instance, have a dynamic DHCP served address, and a remote GUI could also have a dynamic address, but since both initiate the call to the MQTT server, this does not matter.

It allows monitoring of the communications by a third device or service by simply subscribing to the topic used. This makes a possible instrument data broadcasting or logging service easy to implement.

It makes out-of-band communications easy, for example, if other none-INDI communications are needed between devices, then merely subscribing and publishing with another topic is possible.

A disadvantage may be a loss of throughput and response times. An extra layer of communications plus networking is involved, so this may not be suitable for all scenarios.

Though multiple clients connected to the MQTT network is possible, and useful if they are just gathering data, two clients attempting to simultaneously control one instrument would lead to chaos and confusion! A single controlling client would need to be enforced. 

## Security

Only open communications are defined in this package, security and authentication are not considered.

The web service provided here does not apply any authentication.

## Documentation

Detailed information is available at:

https://indiredis.readthedocs.io


