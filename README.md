# indimqttredis

Python indi client package, suitable for a web or gui service. With option of MQTT transmission.

indi - Instrument Neutral Distributed Interface, see https://en.wikipedia.org/wiki/Instrument_Neutral_Distributed_Interface

Though indi is used for astronomical observatory use, it can also be used for any instrument control if appropriate indi drivers are available.  This project provides a client, not drivers, nor indiserver. See https://indilib.org/ 

A Python3 package is provided:

### indimqttredis

An indi client with the capability to read data from redis and send it in indi XML format
to indiserver, and can read device properties from indiserver and store them in redis.

A redis server needs to be provided.

This is done to provide a web framework (or other gui) easy access to device properties and settings via redis
key value storage. The gui or web framework is not specified.

Two options are provided :

The data can be parsed and transferred between redis and indiserver on one machine.

or

The data can be transferred between redis and indiserver on different machines by MQTT.

In the first case, the web/gui, redis server, indiserver are all typically running on one machine. The indimqttredis
package would be imported into a script which will provide the indiserver - redis conversion. The MQTT facility will
not be enabled.

In the second case the web/gui, redis server and MQTT server are typically running on one machine (the web server) 
and indiserver is running on a remote machine at the observatory.  A script running indimqttredis will be running
at both sites, and will provide the indiserver-MQTT conversion at the observatory, and MQTT-redis at the web/gui server.
 
Python dependencies from pypi: "pip install redis" and "pip install paho-mqtt"  (all python3 versions)

Server dependencies: A redis server (apt-get install redis-server), and an MQTT server (apt-get install mosquitto)

Within indimqttredis, three sub packages are available which can be used by your own script:

### indimqttredis.indiredis

Converts directly between indiserver (port 7624) and redis, converts indi XML to redis key-value storage.
For example, your script could be:

```
from indimqttredis import indiredis

# define the servers

indi_server = indiredis.indi_server(host='localhost', port=7624)
redis_server = indiredis.redis_server(host='localhost', port=6379, db=0, password='')

# blocking call which runs the service, communicating between indiserver and redis

indiredis.run(indi_server, redis_server)
```

### indimqttredis.indimqtt

Intended to be run on a device at the observatory (a Raspberry pi), together with indiserver or an indi driver.

Receives/transmitts XML data between indiserver on port 7624 and MQTT which sends data to the remote web/gui server.

### indimqttredis.mqttredis

Intended to be run on the server with the gui or web service which can read/write to redis.

Receives XML data from MQTT and converts to redis key-value storage.

Reads data published to redis, and converts to indi XML and sends by MQTT.


The above packages provide the networking element (reading port 7624 and running MQTT clients), they
call on further sub packages within indimqttredis, to do the xml conversion. These sub packages are
not usually directly imported by a client script, but could be if their functionality is needed
separated from the network elements.


### indimqttredis.toxml

A package that reads values published via redis and converts to indi xml strings.


### indimqttredis.fromxml

A package that reads indi xml strings, parses them and places values into redis.


The web service or gui is not specified, typically a web framework would be used to write code that can read
and write to a local redis service. 

### mqtt and redis - why?

redis is used as:

More than one web service process or thread may be running, redis makes data visible to all processes.

As well as simply storing values for other processes to read, redis has a pub/sub functionality, and
the Python bindings that can use it.

Redis key/value storage and publication is extremely easy, most web frameworks already use it.

mqtt is used since it makes out-of-band communications easy, for example, if other none-indi communications are needed between devices, then merely subscribing and publishing with another topic is possible.

There is flexibility in where the mqtt server is sited, it could run on the web server, or on a different machine entirely.

It allows monitoring of the communications by a third device by simply subscribing to the topic used.

A Python MQTT client is freely available.


