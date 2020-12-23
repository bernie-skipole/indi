
"""Defines blocking function driverstomqtt:

       Given the driver executables, runs them and receives/transmits XML data via their stdin/stdout channels
       and sends/receives to MQTT
   """

import sys, collections, threading, asyncio

from time import sleep

from datetime import datetime

import xml.etree.ElementTree as ET

from . import fromindi

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

def _driverstomqtt_on_message(client, userdata, message):
    "Callback when an MQTT message is received"
    sendsnoopdevices = userdata["sendsnoopdevices"]
    sendsnoopproperties = userdata["sendsnoopproperties"]
    if message.topic == userdata["pubsnoopcontrol"]:
        # The message received on the snoop control topic, is one this device has transmitted, ignore it
        return
    try:
        root = ET.fromstring(message.payload.decode("utf-8"))
    except Exception:
        return
    # On receiving a getproperties on snoop_control/#, checks the name, property to be snooped
    if message.topic.startswith(userdata["snoop_control_topic"]+"/"):
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
            if devicename in sendsnoopdevices:
                sendsnoopdevices[devicename].add(remote_mqtt_id)
            else:
                sendsnoopdevices[devicename] = set((remote_mqtt_id,))
        else:
            # Its a snoop device/property request
            if (devicename,propertyname) in sendsnoopproperties:
                sendsnoopproperties[devicename,propertyname].add(remote_mqtt_id)
            else:
                sendsnoopproperties[devicename,propertyname] = set((remote_mqtt_id,))
        # we have received a snoop getProperties from another device via the mqtt server, send it to the drivers
        userdata["datatodriver"].senddata(message.payload, root)
        return
    if message.topic.startswith(userdata["snoopdata"]):
        # This is snoop data sent from other devices connected elsewhere on the mqtt network to this connection
        # having topic "snoop_data_topic/mqtt_id", where mqtt_id is this connection mqtt_id
        userdata["datatodriver"].snoopdata(message.payload, root)
        if root.tag == "delProperty":
            _remove(root, userdata)
        return
    # we have received a message from a connection via the mqtt server, send it to the drivers
    userdata["datatodriver"].senddata(message.payload, root)
 

def _driverstomqtt_on_connect(client, userdata, flags, rc):
    "The callback for when the mqtt client receives a CONNACK response from the MQTT server, renew subscriptions"
    userdata["datatodriver"].clear()  # - start with fresh empty driver buffers

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


def _driverstomqtt_on_disconnect(client, userdata, rc):
    "The MQTT client has disconnected, set userdata['comms'] = False, and clear out any data hanging about in datatodriver"
    userdata['comms'] = False
    userdata["datatodriver"].clear()


def _sendtomqtt(payload, topic, mqtt_client):
    "Gets data which has been received from a driver, and transmits to mqtt"
    result = mqtt_client.publish(topic=topic, payload=payload, qos=2)
    result.wait_for_publish()


class _DriverHandler:

    def __init__(self, loop, userdata, mqtt_client):
        "Sets the userdata"
        self.userdata = userdata
        self.loop = loop
        self.mqtt_client = mqtt_client
        self.topic = userdata["from_indi_topic"] + "/" + userdata["mqtt_id"]
        self.snoop_data_topic = userdata["snoop_data_topic"] + "/"                 # this will always have a remote mqtt_id appended
        self.datatodriver = userdata['datatodriver']
        self.devicedict = userdata['devicedict']
        self.driverlist = userdata["driverlist"]
        self.sendsnoopall = userdata["sendsnoopall"]
        self.sendsnoopdevices = userdata["sendsnoopdevices"]
        self.sendsnoopproperties = userdata["sendsnoopproperties"]


    async def handle_data(self):
        """Create a subprocess for each driver; redirect the standard in, out, err to coroutines"""
        # self.driverlist is a list of _Driver objects
        tasks = []
        for driver in self.driverlist:
            proc = await asyncio.create_subprocess_exec(
                driver.executable,                      # the driver executable to be run
                stdout=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)

            tasks.append(self.reader(proc.stdout, driver))
            tasks.append(self.writer(proc.stdin, driver))
            tasks.append(self.perror(proc.stderr))
            _message(self.topic, self.mqtt_client, f"Driver {driver.executable} started")
            
        _message(self.topic, self.mqtt_client, "Drivers started, waiting for data")
        # with a whole load of tasks for each driver - readers, writers and error printers, now gather and run them 'simultaneously'
        await asyncio.gather(*tasks)


    async def reader(self, stdout, driver):
        """Reads data from stdout which is the output stream of the driver
           and send it via _sendtomqtt"""
        # get read data from driver, and put it into message
        message = b''
        messagetagnumber = None
        while True:
            # get blocks of data from the driver
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
                    # check if data read is a b'<getProperties ... />' snooping request
                    if data.startswith(b'<getProperties '):
                        # sets flags in the driver that it is snooping
                        try:
                            root = ET.fromstring(data.decode("utf-8"))
                        except Exception:
                            # possible malformed
                            continue
                        driver.setsnoop(root)
                        devicename = root.get("device")
                        if devicename and (devicename in self.devicedict):
                            # its a local devicename, so no need to send getproperties to mqtt, continue with next message
                            continue                    
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
                    # check if this driver is allowed to send BLOBs, or only send BLOBS
                    if driver.checkBlobs(root):
                        devicename = root.get("device")
                        # Run '_sendtomqtt' in the default loop's executor:
                        result = await self.loop.run_in_executor(None, _sendtomqtt, message, self.topic, self.mqtt_client)
                        # if this is to be sent to other drivers via snooping mechanism, then copy the read
                        # message to other drivers inque
                        driver.snoopsend(self.driverlist, message, root)
                        # also may need to be sent to other drivers connected by mqtt
                        for mqtt_id in self.sendsnoopall:
                            # these connections snoop everything
                            snooptopic = self.snoop_data_topic + mqtt_id
                            result = await self.loop.run_in_executor(None, _sendtomqtt, message, snooptopic, self.mqtt_client)
                        if devicename in self.devicedict:
                            if devicename in self.sendsnoopdevices:
                                # list of mqtt_id's which snoop this devicename
                                for mqtt_id in self.sendsnoopdevices[devicename]:
                                    snooptopic = self.snoop_data_topic + mqtt_id
                                    result = await self.loop.run_in_executor(None, _sendtomqtt, message, snooptopic, self.mqtt_client)
                            propertyname = root.get("name")
                            if propertyname:
                                if (devicename,propertyname) in self.sendsnoopproperties:
                                    # list of mqtt_id's which snoop this devicename/propertyname
                                    for mqtt_id in self.sendsnoopproperties[devicename,propertyname]:
                                        snooptopic = self.snoop_data_topic + mqtt_id
                                        result = await self.loop.run_in_executor(None, _sendtomqtt, message, snooptopic, self.mqtt_client)
                    # and start again, waiting for a new message
                    if devicename and (devicename not in self.devicedict):
                        self.devicedict[devicename] = driver
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
                if driver.checkBlobs(root):
                    devicename = root.get("device")
                    # Run '_sendtomqtt' in the default loop's executor:
                    result = await self.loop.run_in_executor(None, _sendtomqtt, message, self.topic, self.mqtt_client)
                    # if this is to be sent to other drivers via snooping mechanism, then copy the read
                    # message to other drivers inque
                    driver.snoopsend(self.driverlist, message, root)
                    # also may need to be sent to other drivers connected by mqtt
                    for mqtt_id in self.sendsnoopall:
                        # these connections snoop everything
                        snooptopic = self.snoop_data_topic + mqtt_id
                        result = await self.loop.run_in_executor(None, _sendtomqtt, message, snooptopic, self.mqtt_client)
                    if devicename in self.devicedict:
                        # find the connections which snoop this devicename
                        if devicename in self.sendsnoopdevices:
                            # list of mqtt_id's which snoop this devicename
                            for mqtt_id in self.sendsnoopdevices[devicename]:
                                snooptopic = self.snoop_data_topic + mqtt_id
                                result = await self.loop.run_in_executor(None, _sendtomqtt, message, snooptopic, self.mqtt_client)
                        propertyname = root.get("name")
                        if propertyname:
                            if (devicename,propertyname) in self.sendsnoopproperties:
                                # list of mqtt_id's which snoop this devicename/propertyname
                                for mqtt_id in self.sendsnoopproperties[devicename,propertyname]:
                                    snooptopic = self.snoop_data_topic + mqtt_id
                                    result = await self.loop.run_in_executor(None, _sendtomqtt, message, snooptopic, self.mqtt_client)
                # and start again, waiting for a new message
                if devicename and (devicename not in self.devicedict):
                    self.devicedict[devicename] = driver
                if root.tag == "delProperty":
                    # remove this device/property from snooping records
                    _remove(root, self.userdata)
                message = b''
                messagetagnumber = None

    async def writer(self, stdin, driver):
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

    async def perror(self, stderr):
        """Reads data from the driver stderr"""
        while True:
            data = await stderr.readline()
            print(data.decode('ascii').rstrip())


def driverstomqtt(drivers, mqtt_id, mqttserver, subscribe_list=[]):
    """Blocking call that provides the drivers - mqtt connection. If subscribe list is empty
    then this function subscribes to received data from all remote client mqtt_id's. If it
    contains a list of mqtt_id's, then only subscribes to their data.

    :param drivers: List of executable drivers
    :type drivers: List
    :param mqtt_id: A unique string, identifying this connection
    :type mqtt_id: String
    :type drivers: List
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

    # a list of drivers
    if isinstance(drivers, str):
        driverlist = [ _Driver(drivers) ]
    else:
        driverlist = list( _Driver(driver) for driver in drivers )

    # a dictionary of {devicename: _Driver instance, ...}
    devicedict = {}

    # _DataToDriver object, used to send data to the drivers 
    datatodriver = _DataToDriver(driverlist, devicedict)

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
               "mqtt_id"             : mqtt_id,
               "snoopdata"           : mqttserver.snoop_data_topic + "/" + mqtt_id,
               "snoopcontrol"        : mqttserver.snoop_control_topic + "/#",                         # used to receive other's getproperty
               "pubsnoopcontrol"     : mqttserver.snoop_control_topic + "/" + mqtt_id,   # used when publishing a getproperty
               "datatodriver"        : datatodriver,
               "driverlist"          : driverlist,
               "subscribe_list"      : subscribe_list,

               "devicedict"          : devicedict,            # a dictionary of {devicename: _Driver instance, ...}
               "sendsnoopall"        : set(),                 # a set of mqtt_id's which want all data sent to them
               "sendsnoopdevices"    : {},  # a dictionary of {devicename: set of mqtt_id's, ...}
                                            # which are those connections which snoop the given devicename
               "sendsnoopproperties" : {}   # a dictionary of {(devicename,propertyname): set of mqtt_id's, ...}
                                            # which are those connections which snoop the given device/property
              }

    mqtt_client = mqtt.Client(client_id=mqtt_id, userdata=userdata)
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

    driverconnections = _DriverHandler(loop, userdata, mqtt_client)


    while True:
        try:
            loop.run_until_complete(driverconnections.handle_data())
        except FileNotFoundError as e:
            _message(userdata["from_indi_topic"] + "/" + userdata["mqtt_id"], mqtt_client, str(e))
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


def _remove(root, userdata):
    "A delProperty is received or being sent, remove this device/property from snooping records"
    sendsnoopdevices = userdata["sendsnoopdevices"]
    sendsnoopproperties = userdata["sendsnoopproperties"]
    devicedict = userdata["devicedict"]
    driverlist = userdata["driverlist"]
    if root.tag != "delProperty":
        return
    devicename = root.get("device")
    if not devicename:
        return
    propertyname = root.get("name")
    if propertyname:
        if (devicename,propertyname) in sendsnoopproperties:
            del sendsnoopproperties[devicename,propertyname]
        for driver in driverlist:
            driver.delproperty(devicename,propertyname)
        return
    # devicename only
    if devicename in devicedict:
        del devicedict[devicename]
    if devicename in sendsnoopdevices:
        del sendsnoopdevices[devicename]
    for driver in driverlist:
        driver.deldevice(devicename)


class _Driver:
    "An object holding state information for each driver"

    def __init__(self, driver):
        self.executable = driver
        # inque is a deque used to send data to the device
        self.inque = collections.deque()
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
        "message has been read from this driver, send it to other drivers that are snooping"
        device = root.get("device")    # name of Device
        name = root.get("name")        # name of Property
        for driver in driverlist:
            if driver is self:
                # do not copy data to self
                continue
            driver.snoopreceive(message, device, name)

    def snoopreceive(self, message, device, name):
        "Received snoop data is added to the drivers inque"
        if self.snoopall:
            # this driver snoops everything
            self.append(message)
        elif device is None:
            return
        elif device in self.snoopdevices:
            # this driver snoops this device
            self.append(message)
        elif name is None:
            return
        elif (device,name) in self.snoopproperties:
            # this driver snoops this device,property
            self.append(message)



class _DataToDriver:
    """An object, which receives data, and which in turn sends it 
     on to the required driver inque's which causes the data to be
     transmitted on to the drivers via the DriverHandler.writer coroutine"""

    def __init__(self, driverlist, devicedict):
        self.driverlist = driverlist
        self.devicedict = devicedict

    def senddata(self, data, root):
        "This data is appended to any driver.inque if the message is relevant to that driver"
        devicename = root.get("device")    # name of Device, could be None if the data
                                           # does not specify it
        if root.tag == "enableBLOB":
            if not devicename:
                # a devicename must be associated with a enableBLOB, if not given discard
                return
            # given the name, enable the driver
            if devicename in self.devicedict:
                driver = self.devicedict[devicename]
                driver.setenabled(devicename, root.get("name"), root.text.strip())
            return
        if not devicename:
            # could be a general getProperties, add to all inque's
            for driver in self.driverlist:
                driver.append(data)
        elif devicename in self.devicedict:
            # so a devicename is specified, and the associated driver is known
            driver = self.devicedict[devicename]
            driver.append(data)

    def snoopdata(self, data, root):
        "Incoming snoop data from MQTT is added to the drivers inque"
        device = root.get("device")    # name of Device from the snoop data
        name = root.get("name")        # name of Property
        for driver in self.driverlist:
            # the driver snoopreceive method adds it to the driver inque
            # if the driver is snooping this device/property
            driver.snoopreceive(data, device, name)


    def clear(self):
        "Clears inques"
        for driver in self.driverlist:
            driver.clear()



