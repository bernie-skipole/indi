
"""Defines blocking function inditomqtt:

       Receives XML data from indiserver on port 7624 and publishes via MQTT.
       Receives data from MQTT, and outputs to port 7624 and indiserver.
   """

#
# snooping
#
# Normally every indiserver/device publishes on the from_indi topic (from indi device to the client)
#
# Every device subscribes to snoop_control/#
# and to snoop_data/mqtt_id
#
# If an indiserver/device wants to snoop, it sends a getproperties to snoop_control/mqtt_id where mqtt_id is its own id
#
# All devices receive it, but the sending device, recognising its own id, ignores it.
# All other devices receiving the getproperties on topic snoop_control/#, records the snooping request, and the snooping connection which wants it
#
# When transmitting data, checks if another connection wants to snoop it, if so then it publishes its data to snoop_data/mqtt_id,
# where mqtt_id is the mqtt_id of the originating snooping request
#
# where the device, which is interested in that data, will receive it, as it subscribes to snoop_data/mqtt_id




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

# Global _DEVICESET is a set of device names served by this indiserver
_DEVICESET = set()

# _SENDSNOOPALL is a set of mqtt_id's which want all data sent to them
_SENDSNOOPALL = set()

# _SENDSNOOPDEVICES is a dictionary of {devicename: set of mqtt_id's, ...} which are those connections which snoop the given devicename
_SENDSNOOPDEVICES = {}

# _SENDSNOOPDEVICES is a dictionary of {(devicename,propertyname): set of mqtt_id's, ...} which are those connections which snoop the given device/property
_SENDSNOOPPROPERTIES = {}


# The _TO_INDI dequeue has the right side filled from redis and the left side
# sent to indiserver.

_TO_INDI = collections.deque(maxlen=100)

# _STARTTAGS is a tuple of ( b'<defTextVector', ...  ) data received will be tested to start with such a starttag

_STARTTAGS = tuple(b'<' + tag for tag in fromindi.TAGS)

# _ENDTAGS is a tuple of ( b'</defTextVector>', ...  ) data received will be tested to end with such an endtag

_ENDTAGS = tuple(b'</' + tag + b'>' for tag in fromindi.TAGS)



### MQTT Handlers for inditomqtt

def _inditomqtt_on_message(client, userdata, message):
    "Callback when an MQTT message is received"
    global _TO_INDI, _DEVICESET, _SENDSNOOPALL, _SENDSNOOPDEVICES, _SENDSNOOPPROPERTIES
    if message.topic == userdata["pubsnoopcontrol"]:
        # The message received on the snoop control topic, is one this device has transmitted, ignore it
        return
    # On receiving a getproperties on snoop_control/#, checks the name, property to be snooped
    if message.topic.startswith(userdata["snoop_control_topic"]+"/"):
        try:
            root = ET.fromstring(message.payload.decode("utf-8"))
        except Exception:
            # possible malformed
            return
        if root.tag != "getProperties":
            # only getProperties listenned to on snoop_control_topic
            return
        devicename = root.get("device")
        propertyname = root.get("name")
        if propertyname and (not devicename):
            # illegal
            return
        snooptopic, remote_mqtt_id = message.topic.split("/", maxsplit=1)
        if not devicename:
            # Its a snoop everything request
            _SENDSNOOPALL.add(remote_mqtt_id)
        elif not propertyname:
            # Its a snoop device request
            if devicename in _SENDSNOOPDEVICES:
                _SENDSNOOPDEVICES[devicename].add(remote_mqtt_id)
            else:
                _SENDSNOOPDEVICES[devicename] = set((remote_mqtt_id,))
        else:
            # Its a snoop device/property request
            if (devicename,propertyname) in _SENDSNOOPPROPERTIES:
                _SENDSNOOPPROPERTIES[devicename,propertyname].add(remote_mqtt_id)
            else:
                _SENDSNOOPPROPERTIES[devicename,propertyname] = set((remote_mqtt_id,))
    if message.payload.startswith(b"delProperty"):
        try:
            root = ET.fromstring(message.payload.decode("utf-8"))
        except Exception:
            # possible malformed
            return
        _remove(root)
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
        if userdata["subscribe_list"]:
            # subscribe to those remote id's listed
            subscribe_list = list((userdata["to_indi_topic"] + "/" + remote_id, 2) for remote_id in userdata["subscribe_list"] )
            # gives a list of [(topic1,2),(topic2,2),(topic3,2)]
            client.subscribe( subscribe_list )
        else:
            # subscribe to all remote id's
            client.subscribe( userdata["to_indi_topic"] + "/#", 2 )

        # Every device subscribes to snoop_control/# being the snoop_control topic and all subtopics
        client.subscribe( userdata["snoopcontrol"], 2 )

        # and to snoop_data/mqtt_id
        client.subscribe( userdata["snoopdata"], 2 )

        print(f"""MQTT connected""")
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


async def _rxfromindi(reader, loop, userdata, mqtt_client):
    global _DEVICESET, _SENDSNOOPALL, _SENDSNOOPDEVICES, _SENDSNOOPPROPERTIES
    # get received data, and put it into message
    message = b''
    messagetagnumber = None
    topic = userdata["from_indi_topic"] + "/" + userdata["mqtt_id"]
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
            else:
                # check if data received is a b'<getProperties ... />' snooping request
                if data.startswith(b'<getProperties '):
                    # send a snoop request on topic snoop_control/mqtt_id where mqtt_id is its own id
                    result = await loop.run_in_executor(None, _sendtomqtt, data, userdata["pubsnoopcontrol"], mqtt_client)
                # data is either a getProperties, or does not start with a recognised tag, so ignore it
                # and continue waiting for a valid message start
                continue
            # set this data into the received message
            message = data
            # either further children of this tag are coming, or maybe its a single tag ending in "/>"
            if message.endswith(b'/>'):
                # the message is complete, handle message here
                try:
                    root = ET.fromstring(message.decode("utf-8"))
                except Exception:
                    # possible malformed
                    message = b''
                    messagetagnumber = None
                    continue
                devicename = root.get("device")
                # Run '_sendtomqtt' in the default loop's executor:
                result = await loop.run_in_executor(None, _sendtomqtt, message, topic, mqtt_client)
                # check if this data it to be sent to snooping devices
                for mqtt_id in _SENDSNOOPALL:
                    # these connections snoop everything
                    snooptopic = userdata["snoop_data_topic"] + "/" + mqtt_id
                    result = await loop.run_in_executor(None, _sendtomqtt, message, snooptopic, mqtt_client)
                if devicename in _DEVICESET:
                    if devicename in _SENDSNOOPDEVICES:
                        # list of mqtt_id's which snoop this devicename
                        for mqtt_id in _SENDSNOOPDEVICES[devicename]:
                            snooptopic = userdata["snoop_data_topic"] + "/" + mqtt_id
                            result = await loop.run_in_executor(None, _sendtomqtt, message, snooptopic, mqtt_client)
                    propertyname = root.get("name")
                    if propertyname:
                        if (devicename,propertyname) in _SENDSNOOPPROPERTIES:
                            # list of mqtt_id's which snoop this devicename/propertyname
                            for mqtt_id in _SENDSNOOPPROPERTIES[devicename,propertyname]:
                                snooptopic = userdata["snoop_data_topic"] + "/" + mqtt_id
                                result = await loop.run_in_executor(None, _sendtomqtt, message, snooptopic, mqtt_client)
                # and start again, waiting for a new message
                if devicename:
                    _DEVICESET.add(devicename)
                if root.tag == "delProperty":
                    # remove this device/property from snooping records
                    _remove(root)
                message = b''
                messagetagnumber = None
            # and read either the next message, or the children of this tag
            continue
        # To reach this point, the message is in progress, with a messagetagnumber set
        # keep adding the received data to message, until an endtag is reached
        message += data
        if message.endswith(_ENDTAGS[messagetagnumber]):
            # the message is complete, handle message here
            try:
                root = ET.fromstring(message.decode("utf-8"))
            except Exception:
                # possible malformed
                message = b''
                messagetagnumber = None
                continue
            devicename = root.get("device")
            # Run '_sendtomqtt' in the default loop's executor:
            result = await loop.run_in_executor(None, _sendtomqtt, message, topic, mqtt_client)
            # check if this data it to be sent to snooping devices
            for mqtt_id in _SENDSNOOPALL:
                # these connections snoop everything
                snooptopic = userdata["snoop_data_topic"] + "/" + mqtt_id
                result = await loop.run_in_executor(None, _sendtomqtt, message, snooptopic, mqtt_client)
            if devicename in _DEVICESET:
                if devicename in _SENDSNOOPDEVICES:
                    # list of mqtt_id's which snoop this devicename
                    for mqtt_id in _SENDSNOOPDEVICES[devicename]:
                        snooptopic = userdata["snoop_data_topic"] + "/" + mqtt_id
                        result = await loop.run_in_executor(None, _sendtomqtt, message, snooptopic, mqtt_client)
                propertyname = root.get("name")
                if propertyname:
                    if (devicename,propertyname) in _SENDSNOOPPROPERTIES:
                        # list of mqtt_id's which snoop this devicename/propertyname
                        for mqtt_id in _SENDSNOOPPROPERTIES[devicename,propertyname]:
                            snooptopic = userdata["snoop_data_topic"] + "/" + mqtt_id
                            result = await loop.run_in_executor(None, _sendtomqtt, message, snooptopic, mqtt_client)
            # and start again, waiting for a new message
            if devicename:
                _DEVICESET.add(devicename)
            if root.tag == "delProperty":
                # remove this device/property from snooping records
                _remove(root)
            message = b''
            messagetagnumber = None


async def _indiconnection(loop, userdata, mqtt_client, indiserver):
    "coroutine to create the connection and start the sender and receiver"
    reader, writer = await asyncio.open_connection(indiserver.host, indiserver.port)
    _message(userdata["from_indi_topic"] + "/" + userdata["mqtt_id"], mqtt_client, f"Connected to {indiserver.host}:{indiserver.port}")
    sent = _txtoindi(writer)
    received = _rxfromindi(reader, loop, userdata, mqtt_client)
    await asyncio.gather(sent, received)



def inditomqtt(indiserver, mqtt_id, mqttserver, subscribe_list=[]):
    """Blocking call that provides the indiserver - mqtt connection. If subscribe list is empty
    then this function subscribes to received data from all remote mqtt_id's. If it
    contains a list of mqtt_id's, then only subscribes to their data.

    :param indiserver: Named Tuple providing the indiserver parameters
    :type indiserver: namedtuple
    :param mqtt_id: A unique string, identifying this connection
    :type mqtt_id: String
    :param mqttserver: Named Tuple providing the mqtt server parameters
    :type mqttserver: namedtuple
    :param subscribe_list: List of remote mqtt_id's to subscribe to
    :type subscribe_list: List
    """

    global _TO_INDI

    if not MQTT_AVAILABLE:
        print("Error - Unable to import the Python paho.mqtt.client package")
        sys.exit(1)

    if (not mqtt_id) or (not isinstance(mqtt_id, str)):
        print("Error - An mqtt_id must be given and must be a non-empty string.")
        sys.exit(1)

    # wait for five seconds before starting, to give mqtt and other servers
    # time to start up
    sleep(5)

    print("inditomqtt started")

    # create an mqtt client and connection
    userdata={ "comms"               : False,        # an indication mqtt connection is working
               "to_indi_topic"       : mqttserver.to_indi_topic,
               "from_indi_topic"     : mqttserver.from_indi_topic,
               "snoop_control_topic" : mqttserver.snoop_control_topic,
               "snoop_data_topic"    : mqttserver.snoop_data_topic,
               "mqtt_id"             : mqtt_id,
               "snoopdata"           : mqttserver.snoop_data_topic + "/" + mqtt_id,
               "snoopcontrol"        : mqttserver.snoop_control_topic + "/#",            # used to receive other's getproperty
               "pubsnoopcontrol"     : mqttserver.snoop_control_topic + "/" + mqtt_id,   # used when publishing a getproperty
               "subscribe_list"      : subscribe_list
              }

    mqtt_client = mqtt.Client(client_id=mqtt_id, userdata=userdata)
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
            loop.run_until_complete(_indiconnection(loop, userdata, mqtt_client, indiserver))
        except ConnectionRefusedError:
            _message(mqttserver.from_indi_topic + "/" + userdata["mqtt_id"], mqtt_client, f"Connection refused on {indiserver.host}:{indiserver.port}, re-trying...")
            sleep(5)
        except asyncio.IncompleteReadError:
            _message(mqttserver.from_indi_topic + "/" + userdata["mqtt_id"], mqtt_client, f"Connection failed on {indiserver.host}:{indiserver.port}, re-trying...")
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


def _remove(root):
    "A delProperty is received or being sent, remove this device/property from snooping records"
    global _DEVICESET, _SENDSNOOPDEVICES, _SENDSNOOPPROPERTIES
    if root.tag != "delProperty":
        return
    devicename = root.get("device")
    if not devicename:
        return
    propertyname = root.get("name")
    if propertyname:
        if (devicename,propertyname) in _SENDSNOOPPROPERTIES:
            del _SENDSNOOPPROPERTIES[devicename,propertyname]
        return
    # devicename only
    if devicename in _DEVICESET:
        _DEVICESET.remove(devicename)
    if devicename in _SENDSNOOPDEVICES:
        del _SENDSNOOPDEVICES[devicename]


