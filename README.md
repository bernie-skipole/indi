# indiredis

Python INDI client package. With option of MQTT transmission.

INDI - Instrument Neutral Distributed Interface, see https://en.wikipedia.org/wiki/Instrument_Neutral_Distributed_Interface

Though INDI is used for astronomical instruments, it can also be used for any instrument control if appropriate INDI drivers are available.

This project provides a client, not drivers, nor indiserver. It is assumed that indiserver is installed and running, together with appropriate drivers and connected instruments.

See https://indilib.org/ for these components.

This Python3 package provides an INDI client with the capability to read instrument properties from indiserver (port 7624) and store them in redis, and in the
other direction; can read data published to redis and send it in INDI XML format to indiserver.

This is done to provide a web framework (or other gui) easy access to device properties and settings via redis key value storage. An example web service is provided. Further documentation, including the redis keys used, can be viewed at https://indiredis.readthedocs.io

Two options are provided :

The data can be parsed and transferred between indiserver and redis.

or

The data can be transferred between indiserver and redis via an MQTT server.

With a redis server and indiserver running on localhost, the sample web service can be run with:

python3 -m indiredis path/to/blobfolder

where path/to/blobfolder is a path to a folder of your choice where Binary Large Objects, such as images, will be stored if your instruments create them. The web client can then be viewed from a browser pointing to localhost:8000


