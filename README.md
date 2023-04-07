# indiredis


This Python3 package provides an INDI web client for general Instrument control.

INDI - Instrument Neutral Distributed Interface.

See https://en.wikipedia.org/wiki/Instrument_Neutral_Distributed_Interface

The package does not include indiserver or drivers, but is compatable with them, indiserver is an application (debian package indi-bin) which runs instrument drivers, and listens on port 7624. This client (or other INDI clients), can connect to this port and using an XML based protocol, control the connected instruments.

Though the INDI protocol is generally used for astronomical instruments, it can work with any instrument if appropriate INDI drivers are available.

If this indiredis package is imported it provides functions for running a web client connected to either: an INDI server port; an MQTT server; or directly to INDI instrument drivers.

If indiredis is run with the python -m option, then the web client is started and connects to an INDI server port.

This web client uses a redis database to hold instrument values, so a redis instance is needed, generally running on the same host as indiredis.

 For example:

Your host typically has instruments connected by appropriate drivers and indiserver. For example, in one terminal, run:

> indiserver -v indi_simulator_telescope indi_simulator_ccd

Usage of this client is then:

> python3 -m indiredis /path/to/blobfolder

The directory /path/to/blobfolder should be a path to a directory of your choice, where BLOB's (Binary Large Objects), such as images will be stored, it will be created if it does not exist. Then connecting with a browser to http://localhost:8000 should enable you to view and control the connected instruments.

For further usage information, including setting ports and hosts, try:

> python3 -m indiredis --help


## Installation

Server dependencies: A redis server (For debian systems; apt-get install redis-server), and indiserver with drivers (apt-get install indi-bin).

For debian systems you may need apt-get install python3-pip, and then use whichever variation of the pip command required by your environment, one example being:

> python3 -m pip install indiredis

Or - if you just want to install it with your own user permissions only:

> python3 -m pip install --user indiredis

Using a virtual environment may be preferred, if you need further information on pip and virtual environments, try:

https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

The above pip command should automatically pull in the following packages:

indi-mr - converts between the XML data received via the indiserver port and redis storage

skipole - framework used to build the web pages.

waitress - Python web server.

redis - Python redis client.

paho-mqtt - Python mqtt client.


## Documentation

If the package is imported into your own scripts, it provides functions which can be adapted to your own web server. Detailed information is available at:

https://indiredis.readthedocs.io
