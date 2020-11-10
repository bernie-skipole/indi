
"""Defines blocking function inditomqtt:

       Receives XML data from indiserver on port 7624 and publishes via MQTT.
       Receives data from MQTT, and outputs to port 7624 and indiserver.
   """

import sys, collections, threading, asyncio

from time import sleep

from datetime import datetime

import xml.etree.ElementTree as ET

from . import toindi, fromindi, tools

MQTT_AVAILABLE = True
try:
    import paho.mqtt.client as mqtt
except:
    MQTT_AVAILABLE = False


# The _TO_INDI dequeue has the right side filled from redis and the left side
# sent to indiserver. Limit length to five items - an arbitrary setting

_TO_INDI = collections.deque(maxlen=5)

# _STARTTAGS is a tuple of ( b'<defTextVector', ...  ) data received will be tested to start with such a starttag

_STARTTAGS = tuple(b'<' + tag for tag in fromindi.TAGS)

# _ENDTAGS is a tuple of ( b'</defTextVector>', ...  ) data received will be tested to end with such an endtag

_ENDTAGS = tuple(b'</' + tag + b'>' for tag in fromindi.TAGS)



### MQTT Handlers for inditomqtt

def _inditomqtt_on_message(client, userdata, message):
    "Callback when an MQTT message is received"
    global _TO_INDI
    # we have received a message from the mqtt server, put it into the _TO_INDI buffer
    _TO_INDI.append(message.payload)
 

def _inditomqtt_on_connect(client, userdata, flags, rc):
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


def _inditomqtt_on_disconnect(client, userdata, rc):
    "The MQTT client has disconnected, set userdata['comms'] = False, and clear out any data hanging about in _TO_INDI"
    global _TO_INDI
    userdata['comms'] = False
    _TO_INDI.clear()


def _sendtomqtt(payload, topic, mqtt_client):
    "Gets data which has been received from indi, and transmits to mqtt"
    result = mqtt_client.publish(topic=topic, payload=payload, qos=2)
    result.wait_for_publish()


async def _txtoindi(writer):
    while True:
        if _TO_INDI:
            # Send the next message to the indiserver
            to_indi = _TO_INDI.popleft()
            writer.write(to_indi)
            await writer.drain()
        else:
            # no message to send, do an async pause
            await asyncio.sleep(0.5)


async def _rxfromindi(reader, loop, topic, mqtt_client):
    # get received data, and put it into message
    message = b''
    messagetagnumber = None
    while True:
        # get blocks of data from the indiserver
        try:
            data = await reader.readuntil(separator=b'>')
        except asyncio.LimitOverrunError:
            data = await reader.read(n=32000)
        if not message:
            # data is expected to start with <tag, first strip any newlines
            data = data.strip()
            for index, st in enumerate(_STARTTAGS):
                if data.startswith(st):
                    messagetagnumber = index
                    break
            if messagetagnumber is None:
                # data does not start with a recognised tag, so ignore it
                # and continue waiting for a valid message start
                continue
            # set this data into the received message
            message = data
            # either further children of this tag are coming, or maybe its a single tag ending in "/>"
            if message.endswith(b'/>'):
                # the message is complete, handle message here
                # Run '_sendtomqtt' in the default loop's executor:
                result = await loop.run_in_executor(None, _sendtomqtt, message, topic, mqtt_client)
                # and start again, waiting for a new message
                message = b''
                messagetagnumber = None
            # and read either the next message, or the children of this tag
            continue
        # To reach this point, the message is in progress, with a messagetagnumber set
        # keep adding the received data to message, until an endtag is reached
        message += data
        if message.endswith(_ENDTAGS[messagetagnumber]):
            # the message is complete, handle message here
            # Run '_sendtomqtt' in the default loop's executor:
            result = await loop.run_in_executor(None, _sendtomqtt, message, topic, mqtt_client)
            # and start again, waiting for a new message
            message = b''
            messagetagnumber = None


async def _indiconnection(loop, topic, mqtt_client, indiserver):
    "coroutine to create the connection and start the sender and receiver"
    reader, writer = await asyncio.open_connection(indiserver.host, indiserver.port)
    _message(topic, mqtt_client, f"Connected to {indiserver.host}:{indiserver.port}")
    sent = _txtoindi(writer)
    received = _rxfromindi(reader, loop, topic, mqtt_client)
    await asyncio.gather(sent, received)



def inditomqtt(indiserver, mqttserver):
    """Blocking call that provides the indiserver - mqtt connection

    :param indiserver: Named Tuple providing the indiserver parameters
    :type indiserver: namedtuple
    :param mqttserver: Named Tuple providing the mqtt server parameters
    :type mqttserver: namedtuple
    """

    global _TO_INDI

    if not MQTT_AVAILABLE:
        print("Error - Unable to import the Python paho.mqtt.client package")
        sys.exit(1)

    # wait for five seconds before starting, to give mqtt and other servers
    # time to start up
    sleep(5)

    print("inditomqtt started")

    # create an mqtt client and connection
    userdata={ "comms"           : False,        # an indication mqtt connection is working
               "to_indi_topic"   : mqttserver.to_indi_topic,
               "from_indi_topic" : mqttserver.from_indi_topic }

    mqtt_client = mqtt.Client(userdata=userdata)
    # attach callback function to client
    mqtt_client.on_connect = _inditomqtt_on_connect
    mqtt_client.on_disconnect = _inditomqtt_on_disconnect
    mqtt_client.on_message = _inditomqtt_on_message
    # If a username/password is set on the mqtt server
    if mqttserver.username and mqttserver.password:
        mqtt_client.username_pw_set(username = mqttserver.username, password = mqttserver.password)
    elif mqttserver.username:
        mqtt_client.username_pw_set(username = mqttserver.username)

    # connect to the MQTT server
    mqtt_client.connect(host=mqttserver.host, port=mqttserver.port)
    mqtt_client.loop_start()

    # Now create a loop to tx and rx the indiserver port
    loop = asyncio.get_event_loop()
    while True:
        _TO_INDI.clear()
        _TO_INDI.append(b'<getProperties version="1.7" />')
        try:
            loop.run_until_complete(_indiconnection(loop, mqttserver.from_indi_topic, mqtt_client, indiserver))
        except ConnectionRefusedError:
            _message(mqttserver.from_indi_topic, mqtt_client, f"Connection refused on {indiserver.host}:{indiserver.port}, re-trying...")
            sleep(5)
        except asyncio.IncompleteReadError:
            _message(mqttserver.from_indi_topic, mqtt_client, f"Connection failed on {indiserver.host}:{indiserver.port}, re-trying...")
            sleep(5)
        else:
            loop.close()
            break


def _message(topic, mqtt_client, message):
    "Print and send a message to mqtt, as if a message had been received from indiserver"
    try:
        print(message)
        sendmessage = ET.Element('message')
        sendmessage.set("message", message)
        sendmessage.set("timestamp", datetime.utcnow().isoformat(timespec='seconds'))
        _sendtomqtt(ET.tostring(sendmessage), topic, mqtt_client)
    except Exception:
        pass
    return




