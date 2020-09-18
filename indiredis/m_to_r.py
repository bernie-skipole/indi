
"""Defines blocking function mqtttoredis:

       Receives XML data from MQTT and stores in redis.
       Reads data published via redis, and outputs to MQTT.

   """

import sys, threading

from time import sleep

REDIS_AVAILABLE = True
try:
    import redis
except:
    REDIS_AVAILABLE = False


MQTT_AVAILABLE = True
try:
    import paho.mqtt.client as mqtt
except:
    MQTT_AVAILABLE = False


from . import toindi, fromindi, tools


#mqttserver = MQTTServer('10.34.167.1', 1883, '', '')



### MQTT Handlers for mqtttoredis

def _mqtttoredis_on_message(client, userdata, message):
    "Callback when an MQTT message is received"
    # we have received a message from the indiserver, load it into redis
    fromindi.receive_from_indiserver(message.payload, userdata["rconn"] )
 

def _mqtttoredis_on_connect(client, userdata, flags, rc):
    "The callback for when the client receives a CONNACK response from the MQTT server, renew subscriptions"

    if rc == 0:
        userdata['comms'] = True
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # subscribe to topic userdata["from_indi_topic"]
        client.subscribe( userdata["from_indi_topic"], 2 )
        print("MQTT client connected")
    else:
        userdata['comms'] = False


def _mqtttoredis_on_disconnect(client, userdata, rc):
    "The MQTT client has disconnected, set userdata['comms'] = False"
    userdata['comms'] = False


# Define an object with an append method to be sent to
# to toindi.SenderLoop, which will be used to 'transmit' data


class _SenderToMQTT():

    def __init__(self, mqtt_client, userdata):
        "Sets the client and topic"
        self.mqtt_client = mqtt_client
        self.topic = userdata["to_indi_topic"]
        self.userdata = userdata

    def append(self, data):
        "send the data via mqtt to the remote"
        if self.userdata["comms"]:
            result = self.mqtt_client.publish(topic=self.topic, payload=data, qos=2)
            result.wait_for_publish()
            return
        # however if self.userdata["comms"] is False, then nothing
        # is published, and the data is discarded


def mqtttoredis(mqttserver, redisserver, log_lengths={}):
    "Blocking call that provides the mqtt - redis connection"

    if not MQTT_AVAILABLE:
        print("Error - Unable to import the Python paho.mqtt.client package")
        sys.exit(1)

    if not REDIS_AVAILABLE:
        print("Error - Unable to import the Python redis package")
        sys.exit(1)

    print("mqtttoredis started")

    # wait two seconds before starting, to give mqtt and other servers
    # time to start up
    sleep(2)

    # set up the redis server
    rconn = _open_redis(redisserver)
    # set the prefix to use for redis keys
    fromindi.setup_redis(redisserver.keyprefix, redisserver.to_indi_channel, redisserver.from_indi_channel, log_lengths)

    # on startup, clear all redis keys
    tools.clearredis(rconn, redisserver)

    # create an mqtt client and connection
    userdata={ "comms"           : False,        # an indication mqtt connection is working
               "to_indi_topic"   : mqttserver.to_indi_topic,
               "from_indi_topic" : mqttserver.from_indi_topic,
               "redisserver"     : redisserver,
               "rconn"           : rconn }

    mqtt_client = mqtt.Client(userdata=userdata)
    # attach callback function to client
    mqtt_client.on_connect = _mqtttoredis_on_connect
    mqtt_client.on_disconnect = _mqtttoredis_on_disconnect
    mqtt_client.on_message = _mqtttoredis_on_message
    # If a username/password is set on the mqtt server
    if mqttserver.username and mqttserver.password:
        mqtt_client.username_pw_set(username = mqttserver.username, password = mqttserver.password)
    elif mqttserver.username:
        mqtt_client.username_pw_set(username = mqttserver.username)
    # connect to the server
    mqtt_client.connect(host=mqttserver.host, port=mqttserver.port)

    # create a sender object, with an append method, which, if used, sends the appended
    # data to mqtt
    sender = _SenderToMQTT(mqtt_client, userdata)

    # Create a SenderLoop object, with the sender object and redis connection
    senderloop = toindi.SenderLoop(sender, rconn, redisserver)
    # run senderloop - which is blocking, so run in its own thread
    run_toindi = threading.Thread(target=senderloop)
    # and start senderloop in its thread
    run_toindi.start()

    # now run the MQTT blocking loop
    print("MQTT loop started")
    mqtt_client.loop_forever()




