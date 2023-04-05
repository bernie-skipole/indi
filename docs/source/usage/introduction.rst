Introduction
============


indiredis
^^^^^^^^^

This Python3 package provides an INDI web client for general Instrument control.

INDI - Instrument Neutral Distributed Interface.

The package does not include indiserver or drivers, but is compatable with them, indiserver is an application (debian package indi-bin) which runs instrument drivers, and listens on port 7624. This, or other INDI clients, connect to this port and using an XML based protocol, control the connected instruments.

For further information on INDI, see :ref:`references`.

Though the INDI protocol is generally used for astronomical instruments, it can work with any instrument if appropriate INDI drivers are available.

This indiredis package can be imported which gives functions for running a web client connected to an INDI server port, an MQTT server or directly to INDI instrument drivers. If indiredis is run with the python -m option, then the web client is started and connects to an INDI server port.

This web client uses a redis database to hold instrument values, so a redis instance is needed, generally running on the same host as indiredis.

 For example:

Your host typically has instruments connected by appropriate drivers and indiserver. For example, in one terminal, run::

    indiserver -v indi_simulator_telescope indi_simulator_ccd

Usage of this client is then::

    python3 -m indiredis /path/to/blobfolder


The directory /path/to/blobfolder should be a path to a directory of your choice, where BLOB's (Binary Large Objects), such as images will be stored, it will be created if it does not exist. Then connecting with a browser to http://localhost:8000 should enable you to view and control the connected instruments.

For further usage information, including setting ports and hosts, try::

    python3 -m indiredis --help

If the package is imported it provides functions for creating the web client, and also connecting to an MQTT server - assuming the INDI XML protocol is being passed via MQTT using the indi-mr python package.


Installation
^^^^^^^^^^^^

Server dependencies: A redis server (For debian systems; apt-get install redis-server), and indiserver with drivers (apt-get install indi-bin).

For debian systems you may need apt-get install python3-pip, and then use whichever variation of the pip command required by your environment, one example being:

python3 -m pip install indiredis

Or - if you just want to install it with your own user permissions only:

python3 -m pip install --user indiredis

Using a virtual environment may be preferred, if you need further information on pip and virtual environments, try:

https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

The above pip command should automatically pull in the following packages:

indi-mr - converts between the XML data received via the indiserver port and redis storage

skipole - framework used to build the web pages.

waitress - Python web server.

redis - Python redis client.


Security
^^^^^^^^

Only open communications are defined in this package, security and authentication are not considered.

The web service provided here does not apply any authentication.
