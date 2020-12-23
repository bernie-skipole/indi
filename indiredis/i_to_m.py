
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

# _STARTTAGS is a tuple of ( b'<defTextVector', ...  ) data received will be tested to start with such a starttag
_STARTTAGS = tuple(b'<' + tag for tag in fromindi.TAGS)

# _ENDTAGS is a tuple of ( b'</defTextVector>', ...  ) data received will be tested to end with such an endtag
_ENDTAGS = tuple(b'</' + tag + b'>' for tag in fromindi.TAGS)



### MQTT Handlers for inditomqtt

def _inditomqtt_on_message(client, userdata, message):
    "Callback when an MQTT message is received"

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
            userdata["sendsnoopall"].add(remote_mqtt_id)
        elif not propertyname:
            # Its a snoop device request
            sendsnoopdevices = userdata["sendsnoopdevices"]
            if devicename in sendsnoopdevices:
                sendsnoopdevices[devicename].add(remote_mqtt_id)
            else:
                sendsnoopdevices[devicename] = set((remote_mqtt_id,))
        else:
            # Its a snoop device/property request
            sendsnoopproperties = userdata["sendsnoopproperties"]
            if (devicename,propertyname) in sendsnoopproperties:
                sendsnoopproperties[devicename,propertyname].add(remote_mqtt_id)
            else:
                sendsnoopproperties[devicename,propertyname] = set((remote_mqtt_id,))
    if message.payload.startswith(b"delProperty"):
        try:
            root = ET.fromstring(message.payload.decode("utf-8"))
        except Exception:
            # possible malformed
            return
        _remove(root, userdata)
    # we have received a message from the mqtt server, put it into the data_to_indi buffer
    userdata['data_to_indi'].append(message.payload)
 

def _inditomqtt_on_connect(client, userdata, flags, rc):
    "The callback for when the client receives a CONNACK response from the MQTT server, renew subscriptions"
    userdata['data_to_indi'].clear()  # - start with fresh empty data_to_indi buffer
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
    "The MQTT client has disconnected, set userdata['comms'] = False, and clear out any data hanging about in data_to_indi"
    userdata['comms'] = False
    userdata['data_to_indi'].clear()


def _sendtomqtt(payload, topic, mqtt_client):
    "Gets data which has been received from indi, and transmits to mqtt"
    result = mqtt_client.publish(topic=topic, payload=payload, qos=2)
    result.wait_for_publish()



class _PortHandler:

    def __init__(self, loop, userdata, mqtt_client, indiserver):
        "Sets the userdata"
        self.userdata = userdata
        self.loop = loop
        self.mqtt_client = mqtt_client
        self.indiserver = indiserver
        self.topic = userdata["from_indi_topic"] + "/" + userdata["mqtt_id"]
        self.snoop_data_topic = userdata["snoop_data_topic"] + "/"                 # this will always have a remote mqtt_id appended
        self.data_to_indi = userdata['data_to_indi']
        self.deviceset = userdata['deviceset']
        self.sendsnoopall = userdata["sendsnoopall"]
        self.sendsnoopdevices = userdata["sendsnoopdevices"]
        self.sendsnoopproperties = userdata["sendsnoopproperties"]

    async def handle_data(self):
        reader, writer = await asyncio.open_connection(self.indiserver.host,self.indiserver.port)
        _message(self.topic, self.mqtt_client, f"Connected to {self.indiserver.host}:{self.indiserver.port}")
        await asyncio.gather(self.txtoindi(writer), self.rxfromindi(reader))


    async def txtoindi(self, writer):
        "Pop message from data_to_indi deque, and write it to the port connection"
        while True:
            if self.data_to_indi:
                # Send the next message to the indiserver
                to_indi = self.data_to_indi.popleft()
                writer.write(to_indi)
                await writer.drain()
            else:
                # no message to send, do an async pause
                await asyncio.sleep(0.5)


    async def rxfromindi(self, reader):
        """get data received from the port connection, and call _sendtomqtt to send it to MQTT
           checks if the data received is to be sent to a snooping device, if so, send it"""
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
                else:
                    # check if data received is a b'<getProperties ... />' snooping request
                    if data.startswith(b'<getProperties '):
                        # send a snoop request on topic snoop_control/mqtt_id where mqtt_id is its own id
                        result = await self.loop.run_in_executor(None, _sendtomqtt, data, self.userdata["pubsnoopcontrol"], self.mqtt_client)
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
                    result = await self.loop.run_in_executor(None, _sendtomqtt, message, self.topic, self.mqtt_client)
                    # check if this data it to be sent to snooping devices
                    for mqtt_id in self.sendsnoopall:
                        # these connections snoop everything
                        snooptopic = self.snoop_data_topic + mqtt_id
                        result = await self.loop.run_in_executor(None, _sendtomqtt, message, snooptopic, self.mqtt_client)
                    if devicename in self.deviceset:
                        if devicename in self.sendsnoopdevices:
                            # set of mqtt_id's which snoop this devicename
                            for mqtt_id in self.sendsnoopdevices[devicename]:
                                snooptopic = self.snoop_data_topic + mqtt_id
                                result = await self.loop.run_in_executor(None, _sendtomqtt, message, snooptopic, self.mqtt_client)
                        propertyname = root.get("name")
                        if propertyname:
                            if (devicename,propertyname) in self.sendsnoopproperties:
                                # set of mqtt_id's which snoop this devicename/propertyname
                                for mqtt_id in self.sendsnoopproperties[devicename,propertyname]:
                                    snooptopic = self.snoop_data_topic + mqtt_id
                                    result = await self.loop.run_in_executor(None, _sendtomqtt, message, snooptopic, self.mqtt_client)
                    # and start again, waiting for a new message
                    if devicename:
                        self.deviceset.add(devicename)
                    if root.tag == "delProperty":
                        # remove this device/property from snooping records
                        _remove(root, self.userdata)
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
                result = await self.loop.run_in_executor(None, _sendtomqtt, message, self.topic, self.mqtt_client)
                # check if this data it to be sent to snooping devices
                for mqtt_id in self.sendsnoopall:
                    # these connections snoop everything
                    snooptopic = self.snoop_data_topic + mqtt_id
                    result = await self.loop.run_in_executor(None, _sendtomqtt, message, snooptopic, self.mqtt_client)
                if devicename in self.deviceset:
                    if devicename in self.sendsnoopdevices:
                        # set of mqtt_id's which snoop this devicename
                        for mqtt_id in self.sendsnoopdevices[devicename]:
                            snooptopic = self.snoop_data_topic + mqtt_id
                            result = await self.loop.run_in_executor(None, _sendtomqtt, message, snooptopic, self.mqtt_client)
                    propertyname = root.get("name")
                    if propertyname:
                        if (devicename,propertyname) in self.sendsnoopproperties:
                            # set of mqtt_id's which snoop this devicename/propertyname
                            for mqtt_id in self.sendsnoopproperties[devicename,propertyname]:
                                snooptopic = self.snoop_data_topic + mqtt_id
                                result = await self.loop.run_in_executor(None, _sendtomqtt, message, snooptopic, self.mqtt_client)
                # and start again, waiting for a new message
                if devicename:
                    self.deviceset.add(devicename)
                if root.tag == "delProperty":
                    # remove this device/property from snooping records
                    _remove(root, self.userdata)
                message = b''
                messagetagnumber = None



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


    # The data_to_indi dequeue has the right side filled from redis and the left side
    # sent to indiserver.

    data_to_indi = collections.deque(maxlen=100)

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
               "subscribe_list"      : subscribe_list,
               "data_to_indi"        : data_to_indi,
               "deviceset"           : set(),                 # a set of device names served by this indiserver
               "sendsnoopall"        : set(),                 # a set of mqtt_id's which want all data sent to them
               "sendsnoopdevices"    : {},  # a dictionary of {devicename: set of mqtt_id's, ...}
                                            # which are those connections which snoop the given devicename
               "sendsnoopproperties" : {}   # a dictionary of {(devicename,propertyname): set of mqtt_id's, ...}
                                            # which are those connections which snoop the given device/property
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

    indiconnection = _PortHandler(loop, userdata, mqtt_client, indiserver)

    while True:
        data_to_indi.clear()
        data_to_indi.append(b'<getProperties version="1.7" />')
        try:
            loop.run_until_complete(indiconnection.handle_data())
        except ConnectionRefusedError:
            _message(mqttserver.from_indi_topic + "/" + mqtt_id, mqtt_client, f"Connection refused on {indiserver.host}:{indiserver.port}, re-trying...")
            sleep(5)
        except asyncio.IncompleteReadError:
            _message(mqttserver.from_indi_topic + "/" + mqtt_id, mqtt_client, f"Connection failed on {indiserver.host}:{indiserver.port}, re-trying...")
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


def _remove(root, userdata):
    "A delProperty is received or being sent, remove this device/property from snooping records"
    if root.tag != "delProperty":
        return
    devicename = root.get("device")
    if not devicename:
        return
    propertyname = root.get("name")
    if propertyname:
        sendsnoopproperties = userdata["sendsnoopproperties"]
        if (devicename,propertyname) in sendsnoopproperties:
            del sendsnoopproperties[devicename,propertyname]
        return
    # devicename only
    if devicename in userdata['deviceset']:
        userdata['deviceset'].remove(devicename)
    sendsnoopdevices = userdata["sendsnoopdevices"]
    if devicename in sendsnoopdevices:
        del sendsnoopdevices[devicename]


