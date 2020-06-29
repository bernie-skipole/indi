#!/home/indi/indienv/bin/python3


###################
#
#  indimqtt
#
###################


"""Reads XML strings from MQTT, and outputs them to port 7624 where they are read by indiserver
   Receives XML data from indiserver on port 7624 and transmits by MQTT."""


import sys, collections, socket, selectors

from time import sleep

import paho.mqtt.client as mqtt



# The _TO_INDI dequeue has the right side filled from mqtt and the left side
# sent to indiserver. Limit length to five items - an arbitrary setting

_TO_INDI = collections.deque(maxlen=5)


### MQTT Handlers

def _on_message(client, userdata, message):
    "Callback when an MQTT message is received"
    global _TO_INDI
    # we have received a message for the indiserver, put it into the _TO_INDI buffer
    _TO_INDI.append(message.payload)
 

def _on_connect(client, userdata, flags, rc):
    "The callback for when the client receives a CONNACK response from the MQTT server, renew subscriptions"
    global _TO_INDI
    _TO_INDI.clear()  # - start with fresh empty _TO_INDI buffer
    if rc == 0:
        userdata['comms'] = True
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe( userdata["to_indi_topic"], 2 )
        print("MQTT client connected")
    else:
        userdata['comms'] = False


def _on_disconnect(client, userdata, rc):
    "The MQTT client has disconnected, set userdata['comms'] = False, and clear out any data hanging about in _TO_INDI"
    global _TO_INDI
    userdata['comms'] = False
    _TO_INDI.clear()



def run(indiserver, mqttserver):
    "Blocking call that provides the indiserver - mqtt connection"
    global _TO_INDI

    # wait for five seconds before starting, to give mqtt and other servers
    # time to start up
    sleep(5)

    print("indimqtt started")

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

    # connect to the MQTT server
    mqtt_client.connect(host=mqttserver.host, port=mqttserver.port)
    mqtt_client.loop_start()

    # set up socket connections to the indiserver
    mysel = selectors.DefaultSelector()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((indiserver.host, indiserver.port))
        sock.setblocking(False)

        # Set up the selector to watch for when the socket is ready
        # to send data as well as when there is data to read.
        mysel.register( sock, selectors.EVENT_READ | selectors.EVENT_WRITE )

        print('waiting for I/O')

        # get blocks of data from the indiserver and fill up this list
        _FROM_INDI = []

        while True:

            for key, mask in mysel.select(timeout=0.1):    # blocks for .1 second
                connection = key.fileobj

                if mask & selectors.EVENT_READ:
                    data = connection.recv(1024)
                    if data:
                        # A readable client socket has data
                        _FROM_INDI.append(data)
                elif _FROM_INDI:
                    # no data to read, so gather the data received so far into a string
                    from_indi = b"".join(_FROM_INDI)
                    # and empty the _FROM_INDI list
                    _FROM_INDI.clear()
                    # send the payload via mqtt with topic from_indi_topic
                    result = mqtt_client.publish(topic=mqttserver.from_indi_topic, payload=from_indi, qos=2)
                    result.wait_for_publish()

                if mask & selectors.EVENT_WRITE:
                    if _TO_INDI:
                        # Send the next message to the indiserver
                        to_indi = _TO_INDI.popleft()
                        sock.sendall(to_indi)




