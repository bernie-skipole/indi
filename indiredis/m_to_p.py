
"""Defines blocking function mqtttoport:

       Opens a server port. If a client is connected, receives XML data from MQTT
       and transmits it to the client, if data received from the client, transmitts it to MQTT.
   """

import sys, collections, threading, asyncio

from time import sleep

MQTT_AVAILABLE = True
try:
    import paho.mqtt.client as mqtt
except:
    MQTT_AVAILABLE = False

# This dequeue has the right side filled from data received at the port from the client
# and the left side is popped and published to MQTT.
_TO_MQTT = collections.deque(maxlen=5)


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



# A single instance of this class is used to keep track of connections
# and hold data received from MQTT to send it on to every connected client 

class _Connections:

    def __init__(self):
        # cons is a dictionary of {sockport : (from_mqtt_deque, blobstatus), ...}
        self.cons = {}

    def add_connection(self, sockport):
        self.cons[sockport] = (collections.deque(maxlen=5), "Never")

    def del_connection(self, sockport):
        if sockport in self.cons:
            del self.cons[sockport]

    def append(self, message):
        "Message received from MQTT, append it to each connection deque"
        for queue, blobstatus in self.cons.values():
            queue.append(message)

    def pop(self, sockport):
        "Get next message, if any from sockport deque, if no message return None"
        value = self.cons.get(sockport)
        if value and value[0]:
            return value[0].popleft()

# This instance is filled with data received from MQTT, and for each connection
# the data is popped and written to the port, and hence to the connected client

_FROM_MQTT = _Connections()


### MQTT Handlers for mqtttoport

def _mqtttoport_on_message(client, userdata, message):
    "Callback when an MQTT message is received"
    # we have received a message from attached instruments via MQTT, append it to _FROM_MQTT
    global _FROM_MQTT
    _FROM_MQTT.append(message.payload)
 

def _mqtttoport_on_connect(client, userdata, flags, rc):
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


def _mqtttoport_on_disconnect(client, userdata, rc):
    "The MQTT client has disconnected, set userdata['comms'] = False"
    userdata['comms'] = False


async def _txtoport(writer, sockport):
    "Receive data from mqtt and write to port"
    global _FROM_MQTT
    # sockport is the port integer of the connection
    while True:
        from_mqtt = _FROM_MQTT.pop(sockport)
        if from_mqtt:
            # Send the next message to the port
            writer.write(from_mqtt)
            await writer.drain()
        else:
            # no message to send, do an async pause
            await asyncio.sleep(0.5)


async def _rxfromport(reader):
    "Receive data at the port from the client, and send to mqtt by appending message to _TO_MQTT"
    global _TO_MQTT
    # get received data, and put it into message
    message = b''
    messagetagnumber = None
    while True:
        # get blocks of data from the port
        try:
            data = await reader.readuntil(separator=b'>')
        except asyncio.LimitOverrunError:
            data = await reader.read(n=32000)
        #except asyncio.streams.IncompleteReadError:
        #    break
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
                _TO_MQTT.append(message)
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
            _TO_MQTT.append(message)
            # and start again, waiting for a new message
            message = b''
            messagetagnumber = None



class _SenderToMQTT():
    """This is run in its own thread, monitors the _TO_MQTT deque, and if it contains
    anything, publishes it to MQTT"""

    def __init__(self, mqtt_client, userdata):
        "Sets the client and topic"
        self.mqtt_client = mqtt_client
        self.topic = userdata["to_indi_topic"]
        self.userdata = userdata

    def __call__(self):
        "send the data via mqtt to the remote instruments"
        global _TO_MQTT
        while True:
            if _TO_MQTT and self.userdata["comms"]:
                result = self.mqtt_client.publish(topic=self.topic, payload=_TO_MQTT.popleft(), qos=2)
                result.wait_for_publish()
            else:
                sleep(0.2)



async def handle_data(reader, writer):
    global _FROM_MQTT
    print("INDI client connected")
    sockip, sockport = writer.get_extra_info('socket').getpeername()
    _FROM_MQTT.add_connection(sockport)
    # sockport is the port integer of the connection
    sent = _txtoport(writer, sockport)
    received = _rxfromport(reader)
    task_sent = asyncio.ensure_future(sent)
    task_received = asyncio.ensure_future(received)
    try:
        await asyncio.gather(task_sent, task_received)
    except Exception:
        task_sent.cancel()
        task_received.cancel()
    print("INDI client disconnected")
    _FROM_MQTT.del_connection(sockport)



def mqtttoport(mqtt_id, mqttserver, port=7624):
    """Blocking call that provides the mqtt - redis connection

    :param mqtt_id: A unique string, identifying this connection
    :type mqtt_id: String
    :param mqttserver: Named Tuple providing the mqtt server parameters
    :type mqttserver: namedtuple
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

    # create an mqtt client and connection
    userdata={ "comms"           : False,        # an indication mqtt connection is working
               "to_indi_topic"   : mqttserver.to_indi_topic,
               "from_indi_topic" : mqttserver.from_indi_topic,
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

    # now run the MQTT  loop
    mqtt_client.loop_start()
    print("MQTT loop started")


    # create a callable object, which sends the data to mqtt
    sender = _SenderToMQTT(mqtt_client, userdata)
    # Transmit data to MQTT in another thread when data is appended to _TO_MQTT
    send_to_mqtt = threading.Thread(target=sender)
    send_to_mqtt.start()

    # now create the listenning socket

    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle_data, '127.0.0.1', port, loop=loop)
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



