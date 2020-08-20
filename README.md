# indiredis

Python INDI client package, suitable for a web or gui service. With option of MQTT transmission.

INDI - Instrument Neutral Distributed Interface, see https://en.wikipedia.org/wiki/Instrument_Neutral_Distributed_Interface

Though INDI is used for astronomical observatory use, it can also be used for any instrument control if appropriate INDI
drivers are available.

This project provides a client, not drivers, nor indiserver. It is assumed that indiserver is installed and running at
the observatory.  See https://indilib.org/ for these components.

A Python3 package is provided:

### indiredis

An INDI client with the capability to read device properties from indiserver (port 7624) and store them in redis, and in the
other direction; can read data published to redis and send it in INDI XML format to indiserver.

This is done to provide a web framework (or other gui) easy access to device properties and settings via redis
key value storage. An example web service is provided. As the code for this project is developed, the redis
keys will be defined and documented in the github wiki.

Two options are provided :

The data can be parsed and transferred between indiserver and redis.

or

The data can be transferred between indiserver and redis via an MQTT server.

Python dependencies from pypi: "pip install redis" and, if the MQTT option is required, "pip install paho-mqtt".

If the example web service is to be run, skipole (web framework) and waitress (web server) are needed:

pip install skipole

pip install waitress

(All python3 versions)

Server dependencies: A redis server (apt-get install redis-server), and, if the MQTT option is used, an
MQTT server (apt-get install mosquitto)

The indiredis package provides functions which can be used by your own script:

### indiredis.inditoredis

Converts directly between indiserver (port 7624) and redis, converting indi XML to redis key-value storage.
For example, your Python script to import and run this service could be:

```
from indiredis import inditoredis, indi_server, redis_server

# define the hosts/ports where servers are listenning, these functions return named tuples
# which are required as arguments to inditoredis().

indi_host = indi_server(host='localhost', port=7624)
redis_host = redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_',
                          to_indi_channel='to_indi', from_indi_channel='from_indi')

# blocking call which runs the service, communicating between indiserver and redis

inditoredis(indi_host, redis_host)
```

### indiredis.inditomqtt

Intended to be run on a device at the observatory (a Raspberry pi), together with indiserver.

Receives/transmitts XML data between indiserver on port 7624 and MQTT which sends data to the remote web/gui server.

Example Python script running at the observatory:

```
from indiredis import inditomqtt, indi_server, mqtt_server

# define the hosts/ports where servers are listenning, these functions return named tuples.

indi_host = indi_server(host='localhost', port=7624)
mqtt_host = mqtt_server(host='10.34.167.1', port=1883, username='', password='',
                        to_indi_topic='to_indi', from_indi_topic='from_indi')

# blocking call which runs the service, communicating between indiserver and mqtt

inditomqtt(indi_host, mqtt_host)

```

Substitute your own MQTT server ip address for 10.34.167.1 in the above example.


### indiredis.mqtttoredis

Intended to be run on the server with the gui or web service which can read/write to redis.

Receives XML data from MQTT and converts to redis key-value storage.

Reads data published to redis, and sends by MQTT.

Example Python script running at the web server:
```
from indiredis import mqtttoredis, mqtt_server, redis_server

# define the hosts/ports where servers are listenning, these functions return named tuples.

mqtt_host = mqtt_server(host='10.34.167.1', port=1883, username='', password='',
                        to_indi_topic='to_indi', from_indi_topic='from_indi')
redis_host = redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_',
                          to_indi_channel='to_indi', from_indi_channel='from_indi')

# blocking call which runs the service, communicating between mqtt and redis

mqtttoredis(mqtt_host, redis_host)

```
Substitute your own MQTT server ip address for 10.34.167.1 in the above example.

### indiredis.tools

The tools module is a set of Python functions, which your gui may use if convenient. These read the
indi devices and properties from redis, returning Python lists and dictionaries, and provides
functions to transmit indi commands by publishing to redis.

### indiredis.indiweb

Your own web framework could be used to write code that can read and write to a redis service. However the
package indiredis.indiweb is provided which creates a Python WSGI application that can provide a demonstration
web service.

It requires the 'skipole' package, available from Pypi, and a wsgi web server, such as 'waitress' also available
from Pypi.

Example Python script running the web service:
```
import threading, os, sys

from indiredis import inditoredis, indi_server, redis_server, tools, indiweb

# any wsgi web server can serve the wsgi application produced by
# indiweb.make_wsgi_app, in this example the web server 'waitress' is used

from waitress import serve

# define the hosts/ports where servers are listenning, these functions return named tuples
# which are required as arguments to inditoredis() and to indiweb.make_wsgi_app()

indi_host = indi_server(host='localhost', port=7624)
redis_host = redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_',
                          to_indi_channel='to_indi', from_indi_channel='from_indi')


# call inditoredis - which is blocking, so run in its own thread
run_inditoredis = threading.Thread(target=inditoredis, args=(indi_host, redis_host))
# and start it
run_inditoredis.start()

# The web service needs a redis connection, available in tools
rconn = tools.open_redis(redis_host)
# create a wsgi application, requires named arguments, rconn and redisserver
application = indiweb.make_wsgi_app(rconn=rconn, redisserver=redis_host)

# serve the application with the python waitress web server
serve(application, host='127.0.0.1', port=8000)

```

### mqtt and redis - why?

redis is used as:

More than one web service process or thread may be running, redis makes data visible to all processes.

As well as simply storing values for other processes to read, redis has a pub/sub functionality. When
data is received, indiredis stores it, and publishes a notification on the from_indi_channel, which can
alert a subscribing GUI application that a value has changed.

When the gui wishes to send data, it can publish it on the to_indi_channel, where it will be picked up by
this indiredis service, and sent to indiserver.

Redis key/value storage and publication is extremely easy, most web frameworks already use it.

MQTT is used since it makes out-of-band communications easy, for example, if other none-INDI communications
are needed between devices, then merely subscribing and publishing with another topic is possible.

There is flexibility in where the MQTT server is sited, it could run on the web server, or on a different
machine entirely. This makes it possible to choose the direction of the initial connection - which may be
useful when passing through NAT firewalls.

As devices connect to the MQTT server, only the IP address of the MQTT server needs to be fixed, a device
running indiserver could, for instance, have a dynamic DHCP served address, and a remote GUI could also
have a dynamic address, but since both initiate the call to the MQTT server, this does not matter.

It allows monitoring of the communications by a third device or service by simply subscribing to the topic
used. This makes a possible logging service easy to implement.


### Security

Only open communications is defined in this package, security and authentication is not considered.
Transmission between servers could pass over an encrypted VPN or SSH tunnel. Any such implementation
is not described here.


