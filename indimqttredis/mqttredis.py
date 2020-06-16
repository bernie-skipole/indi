#!/home/indi/indienv/bin/python3


###################
#
#  mqttredis
#
###################


"""Runs a MQTT client and calls toxml and fromxml to parse the xml data
   and store it, or read it from, redis"""


import sys, collections, threading

from time import sleep

import paho.mqtt.client as mqtt

from . import toxml, fromxml


### MQTT Handlers

def _on_message(client, userdata, message):
    "Callback when an MQTT message is received"
    # we have received a message from the indiserver
    fromxml.receive_from_indiserver(message.payload)
 

def _on_connect(client, userdata, flags, rc):
    "The callback for when the client receives a CONNACK response from the MQTT server, renew subscriptions"

    if rc == 0:
        userdata['comms'] = True
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # subscribe to topic "FomIndiServer/#"
        client.subscribe( userdata["from_indi_topic"], 2 )
        print("MQTT client connected")
    else:
        userdata['comms'] = False


def _on_disconnect(client, userdata, rc):
    "The MQTT client has disconnected, set userdata['comms'] = False"
    userdata['comms'] = False


# Define a callable object to be sent to toxml.sender(), which will be used to 'transmit' data
# this is done to separate the toxml module from MQTT, so, for example, a different network mechanism
# could be used.

class SenderToIndiServer():

    def __init__(self, mqtt_client, userdata):
        "Sets the client and topic"
        self.mqtt_client = mqtt_client
        self.topic = userdata["to_indi_topic"]
        self.userdata = userdata

    def __call__(self, data):
        "send the data via mqtt to the remote"
        if self.userdata["comms"]:
            result = self.mqtt_client.publish(topic=self.topic, payload=data, qos=2)
            result.wait_for_publish()
            return
        # however if self.userdata["comms"] is False, then nothing
        # is published, and the data is discarded


def run(redisserver, mqttserver):
    "Blocking call that provides the redisserver - mqtt connection"

    # wait for five seconds before starting, to give mqtt and other servers
    # time to start up
    sleep(5)

    print("mqttredis started")

    # create an mqtt client and connection
    userdata={ "comms"           : False,        # an indication mqtt connection is working
               "to_indi_topic"   : mqttserver.to_indi_topic,
               "from_indi_topic" : mqttserver.from_indi_topic }

    mqtt_client = mqtt.Client(userdata=userdata)
    # attach callback function to client
    mqtt_client.on_connect = _on_connect
    mqtt_client.on_disconnect = _on_disconnect
    mqtt_client.on_message = _on_message
    # If a username/password is set on the mqtt server
    if mqttserver.username and mqttserver.password:
        mqtt_client.username_pw_set(username = mqttserver.username, password = mqttserver.password)
    elif mqttserver.username:
        mqtt_client.username_pw_set(username = mqttserver.username)
    # connect to the server
    mqtt_client.connect(host=mqttserver.host, port=mqttserver.port)
    # register an instance of SenderToIndiServer with toxml
    toxml.sender(SenderToIndiServer(mqtt_client, userdata))
    # run toxml.loop - which is blocking, so run in its own thread
    run_toxml = threading.Thread(target=toxml.loop)
    # and start toxml.loop in its thread
    run_toxml.start()
    # now run the MQTT blocking loop
    print("MQTT loop started")
    mqtt_client.loop_forever()



