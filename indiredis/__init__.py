
"""Defines functions to create named tuples for the indi, redis and mqtt servers
   used by indiredis.

   Provides blocking functions used to run the service:

   inditoredis:
       Receives XML data from indiserver on port 7624 and stores in redis.
       Reads data published via redis, and outputs to port 7624 and indiserver.

   inditomqtt:
       Receives XML data from indiserver on port 7624 and publishes via MQTT.
       Receives data from MQTT, and outputs to port 7624 and indiserver.

   mqtttoredis:
       Receives XML data from MQTT and stores in redis.
       Reads data published via redis, and outputs to MQTT.

   """

import collections


# make the functions inditoredis, inditomqtt, mqtttoredis available to scripts importing this module
from .i_to_r import inditoredis
from .i_to_m import inditomqtt
from .m_to_r import mqtttoredis


# define namedtuples to hold server parameters

IndiServer = collections.namedtuple('IndiServer', ['host', 'port'])
RedisServer = collections.namedtuple('RedisServer', ['host', 'port', 'db', 'password', 'keyprefix', 'to_indi_channel', 'from_indi_channel'])
MQTTServer = collections.namedtuple('MQTTServer', ['host', 'port', 'username', 'password', 'to_indi_topic', 'from_indi_topic'])


#mqttserver = MQTTServer('10.34.167.1', 1883, '', '')


# Functions which return the appropriate named tuple. Provides defaults and enforces values

def indi_server(host='localhost', port=7624):
    "Creates a named tuple to hold indi server parameters"
    if (not port) or (not isinstance(port, int)):
        raise ValueError("The port must be an integer, 7624 is default")
    return IndiServer(host, port)

def redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_', to_indi_channel='', from_indi_channel=''):
    "Creates a named tuple to hold redis server parameters"
    if (not to_indi_channel) or (not from_indi_channel) or (to_indi_channel == from_indi_channel):
        raise ValueError("Redis channels must exist and must be different from each other.")
    if (not port) or (not isinstance(port, int)):
        raise ValueError("The port must be an integer, 6379 is default")
    return RedisServer(host, port, db, password, keyprefix, to_indi_channel, from_indi_channel)

def mqtt_server(host='localhost', port=1883, username='', password='', to_indi_topic='', from_indi_topic=''):
    "Creates a named tuple to hold mqtt server parameters"
    if (not to_indi_topic) or (not from_indi_topic) or (to_indi_topic == from_indi_topic):
        raise ValueError("MQTT topics must exist and must be different from each other.")
    if (not port) or (not isinstance(port, int)):
        raise ValueError("The port must be an integer, 1883 is default")
    return MQTTServer(host, port, username, password, to_indi_topic, from_indi_topic)







