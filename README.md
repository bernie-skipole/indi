# indiredis

This Python3 package provides an INDI client with the capability to read instrument properties from indiserver (port 7624) and store them in redis, and in the
other direction; can read data published to redis and send it in INDI XML format to indiserver. If the package is run, it provides instrument control via a web service. If imported, it provides tools to read/write to redis, and hence indiserver, for use by your own GUI or WEB applications.

The package is a client only, it does not include indiserver or drivers.

INDI - Instrument Neutral Distributed Interface, see https://en.wikipedia.org/wiki/Instrument_Neutral_Distributed_Interface

Though INDI is used for astronomical instruments, it can also be used for any instrument control if appropriate INDI drivers are available.

Your host should have a redis server running, and indiserver should also be running, together with appropriate drivers and connected instruments. For example, prior to running indiredis, in another terminal, run:

indiserver -v indi_simulator_telescope indi_simulator_ccd

Usage is then:

python3 -m indiredis /path/to/blobfolder


The directory /path/to/blobfolder should be a path to a directory of your choice, where BLOB's (Binary Large Objects), such as images are stored, it will be created if it does not exist. Then connecting with a browser to http://localhost:8000 should enable you to view and control the connected instruments.

For further usage information, including setting ports and hosts, try:

python3 -m indiredis --help

indiredis can be imported into your own scripts, rather than executed with python3 -m. This is particularly aimed at helping the developer create their own GUI's or controlling scripts, perhaps more specialised than the web client included.

Two options are available:

The data can be transferred between indiserver and redis.

or

The data can be transferred between indiserver and redis via an MQTT server.

Further information is availble at:

https://indiredis.readthedocs.io


