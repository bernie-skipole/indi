Introduction
============


The indiredis package
^^^^^^^^^^^^^^^^^^^^^

This Python3 package provides an INDI web client for general Instrument control.

INDI - Instrument Neutral Distributed Interface.

The package does not include indiserver or drivers, but is compatable with them.

For further information on INDI, see :ref:`references`.

Though INDI is generally used for astronomical instruments, it can work with any instrument if appropriate INDI drivers are available.

Your host should have a redis server running, typically with instruments connected by appropriate drivers and indiserver. For example, in one terminal, run::

    indiserver -v indi_simulator_telescope indi_simulator_ccd

Usage of this client is then::

    python3 -m indiredis /path/to/blobfolder


The directory /path/to/blobfolder should be a path to a directory of your choice, where BLOB's (Binary Large Objects), such as images will be stored, it will be created if it does not exist. Then connecting with a browser to http://localhost:8000 should enable you to view and control the connected instruments.

For further usage information, including setting ports and hosts, try::

    python3 -m indiredis --help


Installation
^^^^^^^^^^^^

Server dependencies: A redis server (For debian systems; apt-get install redis-server), and indiserver with drivers (apt-get install indi-bin).

For debian systems you may need apt-get install python3-pip, and then use whichever variation of the pip command required by your environment, one example being:

python3 -m pip install indiredis

Using a virtual environment may be preferred, if you need further information on pip and virtual environments, try:

https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

The above pip command should automatically pull in the following packages:

indi-mr - converts between the XML data received via the indiserver port and redis storage

skipole - required for the built in web service, not needed if you are making your own GUI

waitress - Python web server, not needed if you are creating your own gui, or using a different web server.

redis - Python redis client, needed.


Security
^^^^^^^^

Only open communications are defined in this package, security and authentication are not considered.

The web service provided here does not apply any authentication.


