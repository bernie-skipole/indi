
"""Defines functions to create named tuples for the indi, redis and mqtt servers
   used by indimqttredis.

   These functions include error checking to help ensure the input parameters are
   correct.

   Receives XML data from indiserver on port 7624 and stores in redis.

   Reads data from redis, and outputs to port 7624 and indiserver
   """

import sys, collections, socket, selectors, threading

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


from . import toxml, fromxml, parsetypes



# The _TO_INDI dequeue has the right side filled from redis and the left side
# sent to indiserver. Limit length to five items - an arbitrary setting

_TO_INDI = collections.deque(maxlen=5)


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
    if not REDIS_AVAILABLE:
        print("Error - Unable to import the Python redis package")
        sys.exit(1)
    if (not port) or (not isinstance(port, int)):
        raise ValueError("The port must be an integer, 6379 is default")
    return RedisServer(host, port, db, password, keyprefix)

def mqtt_server(host='localhost', port=1883, username='', password='', to_indi_topic='', from_indi_topic=''):
    "Creates a named tuple to hold mqtt server parameters"
    if not MQTT_AVAILABLE:
        print("Error - Unable to import the Python paho.mqtt.client package")
        sys.exit(1)
    if (not to_indi_topic) or (not from_indi_topic) or (to_indi_topic == from_indi_topic):
        raise ValueError("MQTT topics must exist and must be different from each other.")
    if (not port) or (not isinstance(port, int)):
        raise ValueError("The port must be an integer, 1883 is default")
    return MQTTServer(host, port, username, password, to_indi_topic, from_indi_topic)



# Define a callable object to be sent to toxml.sender(), which will be used to 'transmit' data
# to the indiserver

def _sendertoindiserver(data):
    "Appends data to the global deque _TO_INDI which is used to transmit to indiserver"""
    global _TO_INDI
    _TO_INDI.append(data)


def _open_redis(redisserver):
    "Opens a redis connection"
    try:
        # create a connection to redis
        rconn = redis.StrictRedis(host=redisserver.host,
                                  port=redisserver.port,
                                  db=redisserver.db,
                                  password=redisserver.password,
                                  socket_timeout=5)
    except Exception:
        return
    return rconn


def inditoredis(indiserver, redisserver):
    "Blocking call that provides the indiserver - redis conversion"
    global _TO_INDI

    if not REDIS_AVAILABLE:
        print("Error - Unable to import the Python redis package")
        sys.exit(1)

    # wait for five seconds before starting, to give servers
    # time to start up
    sleep(5)

    print("inditoredis started")

    # set up the redis server
    rconn = _open_redis(redisserver)
    # set the prefix to use for redis keys
    parsetypes.set_prefix(redisserver.keyprefix)
    

    # register the function _sendertoindiserver with toxml
    toxml.sender(_sendertoindiserver)
    # run toxml.loop - which is blocking, so run in its own thread
    run_toxml = threading.Thread(target=toxml.loop)
    # and start toxml.loop in its thread
    run_toxml.start()

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
        from_indi_list = []

        while True:

            for key, mask in mysel.select(timeout=0.1):    # blocks for .1 second
                connection = key.fileobj

                if mask & selectors.EVENT_READ:
                    data = connection.recv(1024)
                    if data:
                        # A readable client socket has data
                        from_indi_list.append(data)
                elif from_indi_list:
                    # no data to read, so gather the data received so far into a string
                    from_indi = b"".join(from_indi_list)
                    # and empty the from_indi_list
                    from_indi_list.clear()
                    # send the data to fromxml to parse and store in redis
                    fromxml.receive_from_indiserver(from_indi, rconn)

                if mask & selectors.EVENT_WRITE:
                    if _TO_INDI:
                        # Send the next message to the indiserver
                        to_indi = _TO_INDI.popleft()
                        sock.sendall(to_indi)



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



def inditomqtt(indiserver, mqttserver):
    "Blocking call that provides the indiserver - mqtt connection"
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





