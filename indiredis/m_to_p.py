
"""Defines blocking function mqtttoport:

       Opens a server port. If a client is connected, receives XML data from MQTT
       and transmits it to the client, if data received from the client, transmitts it to MQTT.
   """

import sys, collections, asyncio

from time import sleep

import xml.etree.ElementTree as ET

MQTT_AVAILABLE = True
try:
    import paho.mqtt.client as mqtt
except:
    MQTT_AVAILABLE = False


# All xml data received on the port from the client should be contained in one of the following tags
TAGS = (b'getProperties',
        b'enableBLOB',
        b'newTextVector',
        b'newNumberVector',
        b'newSwitchVector',
        b'newBLOBVector'
       )

# _STARTTAGS is a tuple of ( b'<newTextVector', ...  ) data received will be tested to start with such a starttag
_STARTTAGS = tuple(b'<' + tag for tag in TAGS)

# _ENDTAGS is a tuple of ( b'</newTextVector>', ...  ) data received will be tested to end with such an endtag
_ENDTAGS = tuple(b'</' + tag + b'>' for tag in TAGS)


### MQTT Handlers for mqtttoport

def _mqtttoport_on_message(client, userdata, message):
    "Callback when an MQTT message is received"
    # we have received a message from attached instruments via MQTT, append it to connections
    # so the sockethandler can send this data on to the clients
    connections = userdata["connections"]
    connections.append(message.payload)
 

def _mqtttoport_on_connect(client, userdata, flags, rc):
    "The callback for when the client receives a CONNACK response from the MQTT server, renew subscriptions"
    if rc == 0:
        userdata['comms'] = True
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # subscribe to topic userdata["from_indi_topic"] and any remote mqtt_id's in subscribe_list
        if userdata["subscribe_list"]:
            # subscribe to those remote id's listed
            subscribe_list = list((userdata["from_indi_topic"] + "/" + remote_id, 2) for remote_id in userdata["subscribe_list"] )
            # gives a list of [(topic1,2),(topic2,2),(topic3,2)]
            client.subscribe( subscribe_list )
        else:
            # subscribe to all remote id's
            client.subscribe( userdata["from_indi_topic"] + "/#", 2 )
        print("MQTT client connected")
    else:
        userdata['comms'] = False


def _mqtttoport_on_disconnect(client, userdata, rc):
    "The MQTT client has disconnected, set userdata['comms'] = False"
    userdata['comms'] = False



class _Connections:
    """An instance of this class is used to keep track of client connections on the port
       and hold data received from MQTT to send it on to every connected client"""

    def __init__(self):
        # cons is a dictionary of {connum : (from_mqtt_deque, enabledevices, enableproperties), ...}
        # connection number - connum - is an integer, a new one being set with every new connection
        # enabledevices is a dictionary of {devicename:BLOBstatus,...}
        # enableproperties is a dictionary of {(devicename, propertyname):BLOBstatus,...}
        self.cons = {}
        # self._connum is used to create a new connection number, by being incremented when a new connection is made
        self._connum = 0

    def new_connection(self):
        "Create a new connection, and return the connection number"
        self._connum += 1
        self.cons[self._connum] = (collections.deque(), {}, {})
        return self._connum

    def del_connection(self, connum):
        if connum in self.cons:
            del self.cons[connum]

    def append(self, message):
        "Message received from MQTT, append it to each connection deque to send out of port"
        try:
            root = ET.fromstring(message.decode("utf-8"))
        except Exception:
            # possible malformed
            return
        for value in self.cons.values():
            if self.checkBlobs(value[1], value[2], root):
                # message can be sent on this port
                value[0].append(message)

    def clear(self):
        "clear dequeue buffers"
        for value in self.cons.values():
            value[0].clear()

    def pop(self, connum):
        "Get next message, if any from connum deque, if no message return None"
        value = self.cons.get(connum)
        if value and value[0]:
            return value[0].popleft()

    def set_enableBLOB(self, connum, message):
        "enableBLOB message has arrived on the port from the client, record the enableBLOB status for the connection"
        if connum not in self.cons:
            return
        try:
            root = ET.fromstring(message.decode("utf-8"))
        except Exception:
            # possible malformed
            return
        if root.tag != "enableBLOB":
            return
        device = root.get("device")    # name of Device
        if not device:
            return
        name = root.get("name")        # name of Property
        status = root.text
        # received enableBLOB status must be one of Never or Also or Only
        if status not in ["Never", "Also", "Only"]:
            return
        value = self.cons[connum]
        if name:
            value[2][device,name] = status
        else:
            value[2][device] = status

    def checkBlobs(self, enabledevices, enableproperties, root):
        "Returns True or False, True if the message is accepted, False otherwise"
        device = root.get("device")    # name of Device
        name = root.get("name")        # name of Property
        if name and (not device):
            # illegal
            return False
        if name and ((device, name) in enableproperties):
            value = enableproperties[device, name]
            if root.tag == "setBLOBVector":
                if value == "Never":
                    return False
                else:
                    return True
            else:
                # something other than a BLOB
                if value == "Only":
                    return False
                else:
                    return True
        # device,name may, or may not, be given, but are not in enableproperties
        # so maybe device is in enabledevices
        value = enabledevices.get(device)
        if root.tag == "setBLOBVector":
            if (value == "Only") or (value == "Also"):
                return True
            else:
                # value could be Never, or None - which is equivalent to Never for Blobs
                return False
        else:
            # something other than a BLOB
            if value == "Only":
                # Anything other than a Blob is not allowed
                return False
            else:
                # value could be None, Never or Also = all of which allow non-blobs
                return True


class _SocketHandler:

    def __init__(self, mqtt_client, userdata, loop):
        "Sets the mqtt client and topic"
        self.mqtt_client = mqtt_client
        self.topic = userdata["to_indi_topic"] + "/" + userdata["mqtt_id"]
        self.userdata = userdata
        self.loop = loop
        # self.connections holds data received from MQTT
        self.connections = userdata["connections"]

    def sendtomqtt(self, data):
        "Gets data which has been received from the ports, and transmits to mqtt"
        if self.userdata["comms"]:
            result = self.mqtt_client.publish(topic=self.topic, payload=data, qos=2)
            result.wait_for_publish()

    async def handle_data(self, reader, writer):
        "Callback used by asyncio.start_server, called to handle a client connection"
        # info = writer.get_extra_info('socket').getpeername()
        print("INDI client connected")
        # set a new connection into self.connections
        connum = self.connections.new_connection()
        # connum is an integer, connection number, referring to the connection
        sent = self.txtoport(writer, connum)
        received = self.rxfromport(reader, connum)
        task_sent = asyncio.ensure_future(sent)         ##### later python versions do not use ensure_future here
        task_received = asyncio.ensure_future(received)
        try:
            await asyncio.gather(task_sent, task_received)
        except Exception as e:
            print(e)
            task_sent.cancel()
            task_received.cancel()
        print("INDI client disconnected")
        self.connections.del_connection(connum)


    async def txtoport(self, writer, connum):
        "Receive data from mqtt and write to port"
        # connum is the connection number of the connection
        while True:
            from_mqtt = self.connections.pop(connum)
            if from_mqtt:
                # Send the next message to the port
                writer.write(from_mqtt)
                await writer.drain()
            else:
                # no message to send, do an async pause
                await asyncio.sleep(0.5)


    async def rxfromport(self, reader, connum):
        "Receive data at the port from the client, and send to mqtt"
        # get received data, and put it into message
        message = b''
        messagetagnumber = None
        while True:
            # get blocks of data from the port
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
                    # data does not start with a recognised tag, so ignore it
                    # and continue waiting for a valid message start
                    continue
                # set this data into the received message
                message = data
                # either further children of this tag are coming, or maybe its a single tag ending in "/>"
                if message.endswith(b'/>'):
                    # the message is complete, handle message here
                    result = await self.loop.run_in_executor(None, self.sendtomqtt, message)
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
                if message.startswith(b"<enableBLOB"):
                    # enableBLOB has arrived, record the instruction
                    self.connections.set_enableBLOB(connum, message)
                # and send to the MQTT network
                result = await self.loop.run_in_executor(None, self.sendtomqtt, message)
                # and start again, waiting for a new message
                message = b''
                messagetagnumber = None



def mqtttoport(mqtt_id, mqttserver, subscribe_list=[], port=7624):
    """Blocking call that provides the mqtt - port connection. If subscribe list is empty
    then this function subscribes to received data from all remote mqtt_id's. If it
    contains a list of mqtt_id's, then only subscribes to their data.

    :param mqtt_id: A unique string, identifying this connection
    :type mqtt_id: String
    :param mqttserver: Named Tuple providing the mqtt server parameters
    :type mqttserver: namedtuple
    :param subscribe_list: List of remote mqtt_id's to subscribe to.
    :type subscribe_list: List
    :param port: Port to listen at, default 7624
    :type port: integer
    """

    if not MQTT_AVAILABLE:
        print("Error - Unable to import the Python paho.mqtt.client package")
        sys.exit(1)

    if (not mqtt_id) or (not isinstance(mqtt_id, str)):
        print("Error - An mqtt_id must be given and must be a non-empty string.")
        sys.exit(1)

    print("mqtttoport started")

    # wait two seconds before starting, to give mqtt and other servers
    # time to start up
    sleep(2)

    # A single instance of the _Connections class is used to keep track of client connections
    # on the server port and hold data received from MQTT to send it on to every connected client 

    connections = _Connections()

    # create an mqtt client and connection
    userdata={ "comms"           : False,        # an indication mqtt connection is working
               "mqtt_id"         : mqtt_id,
               "to_indi_topic"   : mqttserver.to_indi_topic,
               "from_indi_topic" : mqttserver.from_indi_topic,
               "subscribe_list"  : subscribe_list,
               "connections"     : connections
             }

    mqtt_client = mqtt.Client(client_id=mqtt_id, userdata=userdata)
    # attach callback function to client
    mqtt_client.on_connect = _mqtttoport_on_connect
    mqtt_client.on_disconnect = _mqtttoport_on_disconnect
    mqtt_client.on_message = _mqtttoport_on_message
    # If a username/password is set on the mqtt server
    if mqttserver.username and mqttserver.password:
        mqtt_client.username_pw_set(username = mqttserver.username, password = mqttserver.password)
    elif mqttserver.username:
        mqtt_client.username_pw_set(username = mqttserver.username)
    # connect to the server
    mqtt_client.connect(host=mqttserver.host, port=mqttserver.port)

    # now run the MQTT loop in its own thread
    mqtt_client.loop_start()
    print("MQTT loop started")


    # event loop for reading/writing to the port
    loop = asyncio.get_event_loop()

    # create a socket handler, the handle_data method of this instance will
    # be the callback used by asyncio.start_server
    handler = _SocketHandler(mqtt_client, userdata, loop)
    coro = asyncio.start_server(handler.handle_data, 'localhost', port, loop=loop)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    while True:
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            break

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()



