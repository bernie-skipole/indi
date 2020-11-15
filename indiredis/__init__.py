
"""
Defines functions to create named tuples for the indi, redis and mqtt servers.

Provides blocking functions used to run the conversion between indiserver and redis storage.

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
MQTTServer = collections.namedtuple('MQTTServer', ['host', 'port', 'username', 'password', 'to_indi_topic', 'from_indi_topic', 'snoop_indi_topic'])


#mqttserver = MQTTServer('10.34.167.1', 1883, '', '', '', '')


# Functions which return the appropriate named tuple. Provides defaults and enforces values

def indi_server(host='localhost', port=7624):
    """Creates a named tuple to hold indi server parameters

    :param host: The name or ip address of the indiserver, defaults to localhost
    :type host: String
    :param port: The port number of the indiserver, defaults to standard port 7624
    :type port: Integer
    :return: A named tuple with host and port named elements
    :rtype: collections.namedtuple
    """
    if (not port) or (not isinstance(port, int)):
        raise ValueError("The port must be an integer, 7624 is default")
    return IndiServer(host, port)

def redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_', to_indi_channel='to_indi', from_indi_channel='from_indi'):
    """Creates a named tuple to hold redis server parameters

    The to_indi_channel string is used as the channel which a client can use to publish data to redis and hence to
    indiserver. It can be any string you prefer which does not clash with any other channels you may be using with redis.

    The from_indi_channel string must be different from the to_indi_channel string. It is used as the channel on
    which received XML data is published which the client can optionally listen to.

    :param host: The name or ip address of the redis server, defaults to localhost
    :type host: String
    :param port: The port number of the redis server, defaults to standard port 6379
    :type port: Integer
    :param db: The redis database, defaults to 0
    :type db: Integer
    :param password: The redis password, defaults to none used.
    :type password: String
    :param keyprefix: A string to use as a prefix on all redis keys created.
    :type keyprefix: String
    :param to_indi_channel: Redis channel used to publish data to indiserver.
    :type to_indi_channel: String
    :param from_indi_channel: Redis channel used to publish alerts.
    :type from_indi_channel: String
    :return: A named tuple with above parameters as named elements
    :rtype: collections.namedtuple
    """
    if (not to_indi_channel) or (not from_indi_channel) or (to_indi_channel == from_indi_channel):
        raise ValueError("Redis channels must exist and must be different from each other.")
    if (not port) or (not isinstance(port, int)):
        raise ValueError("The port must be an integer, 6379 is default")
    return RedisServer(host, port, db, password, keyprefix, to_indi_channel, from_indi_channel)

def mqtt_server(host='localhost', port=1883, username='', password='', to_indi_topic='to_indi', from_indi_topic='from_indi', snoop_indi_topic='snoop_indi'):
    """Creates a named tuple to hold MQTT server parameters

    The to_indi_topic string is used as the MQTT topic which publishes data to indiserver.
    It can be any string you prefer which does not clash with any other topic you may be using with MQTT.

    The from_indi_topic string must be different from the to_indi_topic string. It is used as the channel on
    which data is sent from indiserver towards the redis server.

    :param host: The name or ip address of the mqtt server, defaults to localhost
    :type host: String
    :param port: The port number of the mqtt server, defaults to standard port 1883
    :type port: Integer
    :param username: The mqtt username, defaults to none used
    :type username: String
    :param password: The mqtt password, defaults to none used.
    :type password: String
    :param to_indi_topic: A string to use as the mqtt topic to send data towards indiserver.
    :type to_indi_topic: String
    :param from_indi_topic: A string to use as the mqtt topic to send data towards redis.
    :type from_indi_topic: String
    :param snoop_indi_topic: This MQTT client subscribes to subtopics snoop_indi/#
    :type snoop_indi_topic: String
    :return: A named tuple with above parameters as named elements
    :rtype: collections.namedtuple
    """
    if (not to_indi_topic) or (not from_indi_topic) or (to_indi_topic == from_indi_topic):
        raise ValueError("MQTT topics must exist and must be different from each other.")

    if (not snoop_indi_topic) or (snoop_indi_topic == to_indi_topic) or (snoop_indi_topic == from_indi_topic):
        raise ValueError("MQTT topics must exist and must be different from each other.")

    if (not port) or (not isinstance(port, int)):
        raise ValueError("The port must be an integer, 1883 is default")
    return MQTTServer(host, port, username, password, to_indi_topic, from_indi_topic, snoop_indi_topic)







