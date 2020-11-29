
"""Defines blocking function driverstomqtt:

       Given the driver executables, runs them and receives/transmits XML data via their stdin/stdout channels
       and sends/receives to MQTT
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

# Global _DRIVERDICT is a dictionary of {devicename: _Driver instance, ...}
_DRIVERDICT = {}

# _SENDSNOOPALL is a set of clientid's which want all data sent to them
_SENDSNOOPALL = set()

# _SENDSNOOPDEVICES is a dictionary of {devicename: set of clientid's, ...} which are those clients which snoop the given devicename
_SENDSNOOPDEVICES = {}

# _SENDSNOOPDEVICES is a dictionary of {(devicename,propertyname): set of clientid's, ...} which are those clients which snoop the given device/property
_SENDSNOOPPROPERTIES = {}

# _STARTTAGS is a tuple of ( b'<defTextVector', ...  ) data received will be tested to start with such a starttag

_STARTTAGS = tuple(b'<' + tag for tag in fromindi.TAGS)

# _ENDTAGS is a tuple of ( b'</defTextVector>', ...  ) data received will be tested to end with such an endtag

_ENDTAGS = tuple(b'</' + tag + b'>' for tag in fromindi.TAGS)



### MQTT Handlers for inditomqtt

def _driverstomqtt_on_message(client, userdata, message):
    "Callback when an MQTT message is received"
    global _DRIVERDICT, _SENDSNOOPALL, _SENDSNOOPDEVICES, _SENDSNOOPPROPERTIES
    if message.topic == userdata["pubsnoopcontrol"]:
        # The message received on the snoop control topic, is one this device has transmitted, ignore it
        return
    # On receiving a getproperties on snoop_control/#, checks the name, property to be snooped
    if message.topic.startswith(userdata["snoop_control_topic"]+"/"):
        root = ET.fromstring(message.payload.decode("utf-8"))
        if root.tag != "getProperties":
            # only getProperties listenned to on snoop_control_topic
            return
        devicename = root.get("device")
        propertyname = root.get("name")
        if propertyname and (not devicename):
            # illegal
            return
        snooptopic, remote_client_id = message.topic.split("/", maxsplit=1)
        if not devicename:
            # Its a snoop everything request
            _SENDSNOOPALL.add(remote_client_id)
        elif not propertyname:
            # Its a snoop device request
            if devicename in _SENDSNOOPDEVICES:
                _SENDSNOOPDEVICES[devicename].add(remote_client_id)
            else:
                _SENDSNOOPDEVICES[devicename] = set((remote_client_id,))
        else:
            # Its a snoop device/property request
            if (devicename,propertyname) in _SENDSNOOPPROPERTIES:
                _SENDSNOOPPROPERTIES[devicename,propertyname].add(remote_client_id)
            else:
                _SENDSNOOPPROPERTIES[devicename,propertyname] = set((remote_client_id,))
    if message.payload.startswith(b"delProperty"):
        root = ET.fromstring(message.payload.decode("utf-8"))
        _remove(userdata["driverlist"], root)
    # we have received a message from the mqtt server, put it into the drivers buffer
    userdata["sender"].append(message.payload)
 

def _driverstomqtt_on_connect(client, userdata, flags, rc):
    "The callback for when the client receives a CONNACK response from the MQTT server, renew subscriptions"

    userdata["sender"].clear()  # - start with fresh empty driver buffers
    if rc == 0:
        userdata['comms'] = True
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe( userdata["to_indi_topic"], 2 )

        # Every device subscribes to snoop_control/# being the snoop_contol topic and all subtopics
        client.subscribe( userdata["snoopcontrol"], 2 )

        # and to snoop_data/client_id
        client.subscribe( userdata["snoopdata"], 2 )

        print(f"""MQTT client connected. Subscribed to:
{userdata["to_indi_topic"]} - Receiving data from clients
{userdata["snoopcontrol"]} - Receiving snoop getProperties from other devices
{userdata["snoopdata"]} - Receiving snooped data sent to this device by other devices""")
    else:
        userdata['comms'] = False


def _driverstomqtt_on_disconnect(client, userdata, rc):
    "The MQTT client has disconnected, set userdata['comms'] = False, and clear out any data hanging about in sender"
    userdata['comms'] = False
    userdata["sender"].clear()


def _sendtomqtt(payload, topic, mqtt_client):
    "Gets data which has been received from a driver, and transmits to mqtt"
    result = mqtt_client.publish(topic=topic, payload=payload, qos=2)
    result.wait_for_publish()


async def _reader(stdout, driver, driverlist, loop, userdata, mqtt_client):
    """Reads data from stdout which is the output stream of the driver
       and send it via _sendtomqtt"""
    global _DRIVERDICT, _SENDSNOOPALL, _SENDSNOOPDEVICES, _SENDSNOOPPROPERTIES
    # get received data, and put it into message
    message = b''
    messagetagnumber = None
    topic = userdata["from_indi_topic"]
    while True:
        # get blocks of data from the indiserver
        try:
            data = await stdout.readuntil(separator=b'>')
        except asyncio.LimitOverrunError:
            data = await stdout.read(n=32000)
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
                    # sets flags in the driver that it is snooping
                    root = ET.fromstring(data)
                    driver.setsnoop(root)
                    devicename = root.get("device")
                    if devicename and (devicename in _DRIVERDICT):
                        # its a local devicename, so no need to send getproperties to mqtt
                        continue                    
                    # send a snoop request on topic snoop_control/client_id where client_id is its own id
                    result = await loop.run_in_executor(None, _sendtomqtt, data, userdata["pubsnoopcontrol"], mqtt_client)
                # data is either a getProperties, or does not start with a recognised tag, so ignore it
                # and continue waiting for a valid message start
                continue
            # set this data into the received message
            message = data
            # either further children of this tag are coming, or maybe its a single tag ending in "/>"
            if message.endswith(b'/>'):
                # the message is complete, handle message here
                root = ET.fromstring(message.decode("utf-8"))
                devicename = root.get("device")
                # Run '_sendtomqtt' in the default loop's executor:
                result = await loop.run_in_executor(None, _sendtomqtt, message, topic, mqtt_client)
                # check if this data it to be sent to snooping devices
                for client_id in _SENDSNOOPALL:
                    snooptopic = userdata["snoop_data_topic"] + "/" + client_id
                    result = await loop.run_in_executor(None, _sendtomqtt, message, snooptopic, mqtt_client)
                if devicename in _DRIVERDICT:
                    if devicename in _SENDSNOOPDEVICES:
                        for client_id in _SENDSNOOPDEVICES[devicename]:
                            snooptopic = userdata["snoop_data_topic"] + "/" + client_id
                            result = await loop.run_in_executor(None, _sendtomqtt, message, snooptopic, mqtt_client)
                    propertyname = root.get("name")
                    if propertyname:
                        if (devicename,propertyname) in _SENDSNOOPPROPERTIES:
                            for client_id in _SENDSNOOPPROPERTIES[devicename,propertyname]:
                                snooptopic = userdata["snoop_data_topic"] + "/" + client_id
                                result = await loop.run_in_executor(None, _sendtomqtt, message, snooptopic, mqtt_client)
                # and start again, waiting for a new message
                if devicename and (devicename not in _DRIVERDICT):
                    _DRIVERDICT[devicename] = driver
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
            root = ET.fromstring(message.decode("utf-8"))
            devicename = root.get("device")
            # Run '_sendtomqtt' in the default loop's executor:
            result = await loop.run_in_executor(None, _sendtomqtt, message, topic, mqtt_client)
            # check if this data it to be sent to snooping devices
            for client_id in _SENDSNOOPALL:
                snooptopic = userdata["snoop_data_topic"] + "/" + client_id
                result = await loop.run_in_executor(None, _sendtomqtt, message, snooptopic, mqtt_client)
            if devicename in _DRIVERDICT:
                if devicename in _SENDSNOOPDEVICES:
                    for client_id in _SENDSNOOPDEVICES[devicename]:
                        snooptopic = userdata["snoop_data_topic"] + "/" + client_id
                        result = await loop.run_in_executor(None, _sendtomqtt, message, snooptopic, mqtt_client)
                propertyname = root.get("name")
                if propertyname:
                    if (devicename,propertyname) in _SENDSNOOPPROPERTIES:
                        for client_id in _SENDSNOOPPROPERTIES[devicename,propertyname]:
                            snooptopic = userdata["snoop_data_topic"] + "/" + client_id
                            result = await loop.run_in_executor(None, _sendtomqtt, message, snooptopic, mqtt_client)
            # and start again, waiting for a new message
            if devicename and (devicename not in _DRIVERDICT):
                _DRIVERDICT[devicename] = driver
            if root.tag == "delProperty":
                # remove this device/property from snooping records
                _remove(root)
            message = b''
            messagetagnumber = None



async def _writer(stdin, driver):
    """Writes data to stdin by reading it from the driver.inque"""
    while True:
        if driver.inque:
            # Send binary xml to the driver stdin
            bxml = driver.inque.popleft()
            stdin.write(bxml)
            await stdin.drain()
        else:
            # no message to send, do an async pause
            await asyncio.sleep(0.5)


async def _perror(stderr):
    """Reads data from the driver stderr"""
    while True:
        data = await stderr.readline()
        print(data.decode('ascii').rstrip())


async def _driverconnections(driverlist, loop, userdata, mqtt_client):
    """Create a subprocess for each driver; redirect the standard in, out, err to coroutines
       driverlist is a list of _Driver objects"""
    tasks = []
    for driver in driverlist:
        proc = await asyncio.create_subprocess_exec(
            driver.executable,                      # the driver executable to be run
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        tasks.append(_reader(proc.stdout, driver, driverlist, loop, userdata, mqtt_client))
        tasks.append(_writer(proc.stdin, driver))
        tasks.append(_perror(proc.stderr))
        _message(rconn, f"Driver {driver.executable} started")
        
    _message(rconn, "Drivers started, waiting for data")
    # with a whole load of tasks for each driver - readers, writers and error printers, now gather and run them 'simultaneously'
    await asyncio.gather(*tasks)




def driverstomqtt(drivers, mqttserver):
    """Blocking call that provides the drivers - mqtt connection

    :param drivers: List of executable drivers
    :type drivers: List
    :param mqttserver: Named Tuple providing the mqtt server parameters
    :type mqttserver: namedtuple
    """

    if not MQTT_AVAILABLE:
        print("Error - Unable to import the Python paho.mqtt.client package")
        sys.exit(1)

    # a list of drivers
    driverlist = list( _Driver(driver) for driver in drivers )

    # sender object, used to append data, and to send it
    sender = _Sender(driverlist)

    # wait for two seconds before starting, to give mqtt and other servers
    # time to start up
    sleep(2)

    print("driverstomqtt started")

    # create an mqtt client and connection
    userdata={ "comms"               : False,        # an indication mqtt connection is working
               "to_indi_topic"       : mqttserver.to_indi_topic,
               "from_indi_topic"     : mqttserver.from_indi_topic,
               "snoop_control_topic" : mqttserver.snoop_control_topic,
               "snoop_data_topic"    : mqttserver.snoop_data_topic,
               "client_id"           : mqttserver.client_id,
               "snoopdata"           : mqttserver.snoop_data_topic + "/" + mqttserver.client_id,
               "snoopcontrol"        : mqttserver.snoop_control_topic + "/#",                         # used to receive other's getproperty
               "pubsnoopcontrol"     : mqttserver.snoop_control_topic + "/" + mqttserver.client_id,   # used when publishing a getproperty
               "sender"              : sender,
               "driverlist"          : driverlist
              }

    mqtt_client = mqtt.Client(client_id=mqttserver.client_id, userdata=userdata)
    # attach callback function to client
    mqtt_client.on_connect = _driverstomqtt_on_connect
    mqtt_client.on_disconnect = _driverstomqtt_on_disconnect
    mqtt_client.on_message = _driverstomqtt_on_message
    # If a username/password is set on the mqtt server
    if mqttserver.username and mqttserver.password:
        mqtt_client.username_pw_set(username = mqttserver.username, password = mqttserver.password)
    elif mqttserver.username:
        mqtt_client.username_pw_set(username = mqttserver.username)

    # connect to the MQTT server
    mqtt_client.connect(host=mqttserver.host, port=mqttserver.port)
    mqtt_client.loop_start()

    # now start eventloop to read and write to the drivers
    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(_driverconnections(driverlist, loop, userdata, mqtt_client))
        except FileNotFoundError as e:
            _message(rconn, str(e))
            sleep(2)
            break
        finally:
            loop.close()


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


def _remove(driverlist, root):
    "A delProperty is received or being sent, remove this device/property from snooping records"
    global _DRIVERDICT, _SENDSNOOPDEVICES, _SENDSNOOPPROPERTIES
    if root.tag != "delProperty":
        return
    devicename = root.get("device")
    if not devicename:
        return
    propertyname = root.get("name")
    if propertyname:
        if (devicename,propertyname) in _SENDSNOOPPROPERTIES:
            del _SENDSNOOPPROPERTIES[devicename,propertyname]
        for driver in driverlist:
            driver.delproperty(devicename,propertyname)
        return
    # devicename only
    if devicename in _DRIVERDICT:
        del _DRIVERDICT[devicename]
    if devicename in _SENDSNOOPDEVICES:
        del _SENDSNOOPDEVICES[devicename]
    for driver in driverlist:
        driver.deldevice(devicename)


class _Driver:
    "An object holding state information for each driver"

    def __init__(self, driver):
        self.executable = driver
        # inque is a deque used to send data to the device
        self.inque = collections.deque(maxlen=10)
        # when initialised, always start with a getProperties
        self.inque.append(b'<getProperties version="1.7" />')
        # Blobs enabled or not
        self.enableproperties = {}
        self.enabledevices = {}
        # flag set to True, if this snoops on all other devices
        self.snoopall = False
        # set of devicenames this driver snoops on
        self.snoopdevices = set()
        # set of (devicenames, propertynames) this driver snoop on
        self.snoopproperties = set()

    def append(self, data):
        "Append data to the driver inque, where it can be read and transmitted to the driver"
        self.inque.append(data)

    def clear(self):
        "Clears the driver inque"
        self.inque.clear()

    def setenabled(self, devicename, propertyname, value):
        "Sets the enableBLOB status for the given devicename, blobname"
        if devicename is None:
            # illegal
            return
        if propertyname:
            self.enableproperties[devicename,propertyname] = value   # Never or Also or Only
        else:
            self.enabledevices[devicename] = value

    def delproperty(self, devicename, propertyname):
        "Deletes property from snooping, and enabled records"
        if (devicename,propertyname) in self.snoopproperties:
            self.snoopproperties.remove((devicename,propertyname))
        if (devicename,propertyname) in self.enableproperties:
            del self.enableproperties[devicename,propertyname]

    def deldevice(self, device):
        "Deletes devicename from snooping, and enabled records"
        if device in self.snoopdevices:
            self.snoopdevices.remove(device)
        for devicename,propertyname in self.snoopproperties:
            if device == devicename:
                self.snoopproperties.remove((devicename,propertyname))
        if device in self.enabledevices:
            del self.enabledevices[device]
        for devicename,propertyname in self.enableproperties:
            if device == devicename:
                del self.enableproperties[devicename,propertyname]

    def checkBlobs(self, root):
        "Returns True or False, True if the message is accepted, False otherwise"
        device = root.get("device")    # name of Device
        name = root.get("name")        # name of Property

        if name and (not device):
            # illegal
            return False

        if name and ((device, name) in self.enableproperties):
            value = self.enableproperties[device, name]
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
           
        # device,name may, or may not, be given, but are not in self.enableproperties
        # so maybe device is in self.enabledevice
        value = self.enabledevices.get(device)
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

    def setsnoop(self, root):
        "data received from the driver starts with b'<getProperties ', so set snooping flags"
        if self.snoopall:
            # already snoops everything, do not have to do anything else
            return
        if root.tag != "getProperties":
            return
        device = root.get("device")    # name of Device
        if device is None:
            # this is a general getProperties request, snoops on everything
            self.snoopall = True
            return
        if device in self.snoopdevices:
            # already snoops on all properties of this device
            return
        name = root.get("name")        # name of Property
        if name is None:
            # must snoop on all properties of this device
            self.snoopdevices.add(device)
        else:
            # must snoop on this device and property
            self.snoopproperties.add((device,name))

    def snoopsend(self, driverlist, message, root):
        "message has been received by this driver, send it to other drivers that are snooping"
        device = root.get("device")    # name of Device
        name = root.get("name")        # name of Property
        for driver in driverlist:
            if driver is self:
                # do not copy data to self
                continue
            if driver.snoopall:
                # this driver snoops everything
                driver.append(message)
            elif device is None:
                continue
            elif device in driver.snoopdevices:
                # this driver snoops this device
                driver.append(message)
            elif name is None:
                continue
            elif (device,name) in driver.snoopproperties:
                # this driver snoops this device,property
                driver.append(message)


class _Sender:
    """An object, with an append method, which gets data appended, which in turn
     gets added here to the required driver inque's which causes the data to be
     transmitted on to the drivers via the _writer coroutine"""

    def __init__(self, driverlist):
        self.driverlist = driverlist

    def append(self, data):
        "This data is appended to any driver.inque if the message is relevant to that driver"
        global _DRIVERDICT
        root = ET.fromstring(data.decode("utf-8"))
        devicename = root.get("device")    # name of Device, could be None if the data
                                           # does not specify it

        if root.tag == "enableBLOB":
            if not devicename:
                # a devicename must be associated with a enableBLOB, if not given discard
                return
            # given the name, enable the driver
            if devicename in _DRIVERDICT:
                driver = _DRIVERDICT[devicename]
                driver.setenabled(devicename, root.get("name"), root.text.strip())
            return

        if not devicename:
            # add to all inque's
            for driver in self.driverlist:
                driver.append(data)
        elif devicename in _DRIVERDICT:
            # so a devicename is specified, and the associated driver is known
            driver = _DRIVERDICT[devicename]
            driver.append(data)
        else:
            # so a devicename is specified, but no driver found, so send it to all
            for driver in self.driverlist:
                driver.append(data)

    def clear(self):
        "Clears inques"
        for driver in self.driverlist:
            driver.clear()



