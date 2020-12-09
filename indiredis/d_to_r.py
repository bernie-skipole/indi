
"""Defines blocking function driverstoredis:
   
       Given the driver executables, runs them and receives/transmits XML data via their stdin/stdout channels
       and stores/publishes via redis.
   """


import os, sys, collections, threading, asyncio, pathlib

from time import sleep

from datetime import datetime

import xml.etree.ElementTree as ET

from . import toindi, fromindi, tools

REDIS_AVAILABLE = True
try:
    import redis
except:
    REDIS_AVAILABLE = False

# Global _DRIVERDICT is a dictionary of {devicename: _Driver instance, ...}

_DRIVERDICT = {}


# _STARTTAGS is a tuple of ( b'<defTextVector', ...  ) data received will be tested to start with such a starttag

_STARTTAGS = tuple(b'<' + tag for tag in fromindi.TAGS)


# _ENDTAGS is a tuple of ( b'</defTextVector>', ...  ) data received will be tested to end with such an endtag

_ENDTAGS = tuple(b'</' + tag + b'>' for tag in fromindi.TAGS)


async def _reader(stdout, driver, driverlist, loop, rconn):
    """Reads data from stdout which is the output stream of the driver
       and send it via fromindi.receive_from_indiserver - which sets data into redis
       and returns the devicename if found.
       the devicename and driver is set into _DRIVERDICT"""
    global _DRIVERDICT

    # get received data, and put it into message
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
                # check if data received is a b'<getProperties ... />' snooping request
                if data.startswith(b'<getProperties '):
                    # sets flags in the driver that it is snooping
                    try:
                        root = ET.fromstring(data.decode("utf-8"))
                    except Exception:
                        # possible malformed
                        continue
                    driver.setsnoop(root)
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
                    message = b''
                    messagetagnumber = None
                    continue
                # if this is to be sent to other devices via snooping mechanism, then copy the read
                # message to other divers inque
                driver.snoopsend(driverlist, message, root)
                if driver.checkBlobs(root):
                    # Run 'fromindi.receive_from_indiserver' in the default loop's executor:
                    devicename = await loop.run_in_executor(None, fromindi.receive_from_indiserver, message, root, rconn)
                    # result is None, or the device name if a defxxxx was received
                    if devicename and (devicename not in _DRIVERDICT):
                        _DRIVERDICT[devicename] = driver
                if root.tag == "delProperty":
                    # remove this device/property from snooping records
                    _remove(driverlist, root)
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
            try:
                root = ET.fromstring(message.decode("utf-8"))
            except Exception:
                message = b''
                messagetagnumber = None
                continue
            # if this is to be sent to other devices via snooping mechanism, then copy the read
            # message to other divers inque
            driver.snoopsend(driverlist, message, root)
            if driver.checkBlobs(root):
                # Run 'fromindi.receive_from_indiserver' in the default loop's executor:
                devicename = await loop.run_in_executor(None, fromindi.receive_from_indiserver, message, root, rconn)
                # result is None, or the device name if a defxxxx was received
                if devicename and (devicename not in _DRIVERDICT):
                    _DRIVERDICT[devicename] = driver
            if root.tag == "delProperty":
                # remove this device/property from snooping records
                _remove(driverlist, root)
            # and start again, waiting for a new message
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


async def _driverconnections(driverlist, loop, rconn):
    """Create a subprocess for each driver; redirect the standard in, out, err to coroutines
       driverlist is a list of _Driver objects"""
    tasks = []
    for driver in driverlist:
        proc = await asyncio.create_subprocess_exec(
            driver.executable,                      # the driver executable to be run
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        tasks.append(_reader(proc.stdout, driver, driverlist, loop, rconn))
        tasks.append(_writer(proc.stdin, driver))
        tasks.append(_perror(proc.stderr))
        _message(rconn, f"Driver {driver.executable} started")
        
    _message(rconn, "Drivers started, waiting for data")
    # with a whole load of tasks for each driver - readers, writers and error printers, now gather and run them 'simultaneously'
    await asyncio.gather(*tasks)



def driverstoredis(drivers, redisserver, log_lengths={}, blob_folder=''):
    """Blocking call that provides the drivers - redis conversion

    :param drivers: List of executable drivers
    :type drivers: List
    :param redisserver: Named Tuple providing the redis server parameters
    :type redisserver: namedtuple
    :param log_lengths: provides number of logs to store
    :type log_lengths: dictionary
    :param blob_folder: Folder where Blobs will be stored
    :type blob_folder: String
    """

    if not REDIS_AVAILABLE:
        print("Error - Unable to import the Python redis package")
        sys.exit(1)

    print("driverstoredis started")

    # wait two seconds before starting, to give servers
    # time to start up
    sleep(2)

    if blob_folder:
        blob_folder = pathlib.Path(blob_folder).expanduser().resolve()
    else:
        print("Error - a blob_folder must be given")
        sys.exit(2)

    # check if the blob_folder exists
    if not blob_folder.exists():
        # if not, create it
        blob_folder.mkdir(parents=True)

    if not blob_folder.is_dir():
        print("Error - blob_folder already exists and is not a directory")
        sys.exit(3)

    # set up the redis server
    rconn = tools.open_redis(redisserver)
    # set the fromindi parameters
    fromindi.setup_redis(redisserver.keyprefix, redisserver.to_indi_channel, redisserver.from_indi_channel, log_lengths, blob_folder)

    # on startup, clear all redis keys
    tools.clearredis(rconn, redisserver)

    # a list of drivers
    if isinstance(drivers, str):
        driverlist = [ _Driver(drivers) ]
    else:
        driverlist = list( _Driver(driver) for driver in drivers )

    # sender object, used to append data, and to send it
    sender = _Sender(driverlist)

    # Create a SenderLoop object, with the _Sender object and redis connection
    senderloop = toindi.SenderLoop(sender, rconn, redisserver)
    # run senderloop - which is blocking, so run in its own thread
    run_sender = threading.Thread(target=senderloop)
    # and start senderloop in its thread
    run_sender.start()

    # now start eventloop to read and write to the drivers

    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(_driverconnections(driverlist, loop, rconn))
        except FileNotFoundError as e:
            _message(rconn, str(e))
            sleep(2)
            break
        finally:
            loop.close()


def _message(rconn, message):
    "Saves a message to redis, as if a message had been received from indiserver"
    try:
        print(message)
        timestamp = datetime.utcnow().isoformat(timespec='seconds')
        message_object = fromindi.Message({'message':message, 'timestamp':timestamp})
        message_object.write(rconn)
        message_object.log(rconn, timestamp)
    except Exception:
        pass
    return


def _remove(driverlist, root):
    "A delProperty has been received, remove the given device/property from snoops and blob enables"
    global _DRIVERDICT
    if root.tag != "delProperty":
        return
    device = root.get("device")    # name of Device
    if device is None:
        # illegal
        return
    name = root.get("name")        # name of Property
    if name:
        for driver in driverlist:
            driver.delproperty(device, name)
        return
    # no property name, remove all mentions of this device name
    if device in _DRIVERDICT:
        del _DRIVERDICT[device]
    for driver in driverlist:
        driver.deldevice(device)


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




class _Sender:
    """An object, with an append method, which gets data appended, which in turn
     gets added here to the required driver inque's which causes the data to be
     transmitted on to the drivers via the _writer coroutine"""

    def __init__(self, driverlist):
        self.driverlist = driverlist

    def append(self, data):
        "This data is appended to any driver.inque if the message is relevant to that driver"
        global _DRIVERDICT
        try:
            root = ET.fromstring(data.decode("utf-8"))
        except Exception:
            # possible malformed
            return
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
            # this could be data from another device meant to be snooped by this device
            # add to all inque's
            for driver in self.driverlist:
                driver.append(data)


    def clear(self):
        "Clears inques"
        for driver in self.driverlist:
            driver.clear()


