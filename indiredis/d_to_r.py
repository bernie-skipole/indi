
"""Defines blocking function driverstoredis:
   
       Given the drivers, runs them and receives/transmits XML data via their stdin/stdout channels
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


async def _reader(stdout, driver, loop, rconn):
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
            if messagetagnumber is None:
                # data does not start with a recognised tag, so ignore it
                # and continue waiting for a valid message start
                continue
            # set this data into the received message
            message = data
            # either further children of this tag are coming, or maybe its a single tag ending in "/>"
            if message.endswith(b'/>'):
                # the message is complete, handle message here
                if _checkBlobs(driver, message):
                    # Run 'fromindi.receive_from_indiserver' in the default loop's executor:
                    devicename = await loop.run_in_executor(None, fromindi.receive_from_indiserver, message, rconn)
                    # result is None, or the device name if a defxxxx was received
                    if devicename and (devicename not in _DRIVERDICT):
                        _DRIVERDICT[devicename] = driver
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
            if _checkBlobs(driver, message):
                # Run 'fromindi.receive_from_indiserver' in the default loop's executor:
                devicename = await loop.run_in_executor(None, fromindi.receive_from_indiserver, message, rconn)
                # result is None, or the device name if a defxxxx was received
                if devicename and (devicename not in _DRIVERDICT):
                    _DRIVERDICT[devicename] = driver
            # and start again, waiting for a new message
            message = b''
            messagetagnumber = None


def _checkBlobs(driver, message):
    "Returns True or False, True if the message is accepted, False otherwise"
    # driver.enabled is one of Never or Also or Only
    if driver.enabled == "Also":
        return True
    root = ET.fromstring(message.decode("utf-8"))
    if root.tag == "setBLOBVector":
        if driver.enabled == "Never":
            return False
        else:
            # driver.enabled must be Only
            return True
    elif driver.enabled == "Only":
        # so not a setBLOBVector, but only setBLOBVector allowed
        return False
    # driver.enabled must be never, but its not a setBLOBVector, so ok
    return True


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

        tasks.append(_reader(proc.stdout, driver, loop, rconn))
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


class _Driver:
    "An object holding state information for each driver"

    def __init__(self, driver):
        self.executable = driver
        # inque is a deque used to send data to the device
        self.inque = collections.deque(maxlen=5)
        # when initialised, always start with a getProperties
        self.inque.append(b'<getProperties version="1.7" />')
        # Blobs enabled or not
        self.enabled = "Never"   # or Also or Only

    def append(self, data):
        "Append data to the driver inque, where it can be read and transmitted to the driver"
        self.inque.append(data)


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

        if root.tag = "BLOBenable":
            if not devicename:
                # a devicename must be associated with a BLOBenable, if not given discard
                return
            # given the name, enable the driver
            if devicename in _DRIVERDICT:
                driver = _DRIVERDICT[devicename]
                driver.enabled = root.text.strip()

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



