
"""Defines functions to create named tuples for the indi, redis and mqtt servers
   used by indimqttredis.

   These functions include error checking to help ensure the input parameters are
   correct
   """


import collections


# define the server parameters

IndiServer = collections.namedtuple('IndiServer', ['host', 'port'])
RedisServer = collections.namedtuple('RedisServer', ['host', 'port', 'db', 'password', 'keyprefix'])
MQTTServer = collections.namedtuple('MQTTServer', ['host', 'port', 'username', 'password', 'to_indi_topic', 'from_indi_topic'])


#mqttserver = MQTTServer('10.34.167.1', 1883, '', '')


def indi_server(host='localhost', port=7624):
    "Creates a named tuple to hold indi server parameters"
    if (not port) or (not isinstance(port, int)):
        raise ValueError("The port must be an integer, 7624 is default")
    return IndiServer(host, port)

def redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_'):
    "Creates a named tuple to hold redis server parameters"
    if (not port) or (not isinstance(port, int)):
        raise ValueError("The port must be an integer, 6379 is default")
    return RedisServer(host, port, db, password, keyprefix)

def mqtt_server(host='localhost', port=1883, username='', password='', to_indi_topic='', from_indi_topic=''):
    "Creates a named tuple to hold mqtt server parameters"
    if (not to_indi_topic) or (not from_indi_topic) or (to_indi_topic == from_indi_topic):
        raise ValueError("MQTT topics must exist and must be different from each other.")
    if (not port) or (not isinstance(port, int)):
        raise ValueError("The port must be an integer, 1883 is default")
    return MQTTServer(host, port, username, password, to_indi_topic, from_indi_topic)


