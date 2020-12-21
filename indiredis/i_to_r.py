
"""Defines blocking function inditoredis:
   
       Receives XML data from indiserver on port 7624 and stores in redis.
       Reads data published via redis, and outputs to port 7624 and indiserver.

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

# _STARTTAGS is a tuple of ( b'<defTextVector', ...  ) data received will be tested to start with such a starttag
_STARTTAGS = tuple(b'<' + tag for tag in fromindi.TAGS)

# _ENDTAGS is a tuple of ( b'</defTextVector>', ...  ) data received will be tested to end with such an endtag
_ENDTAGS = tuple(b'</' + tag + b'>' for tag in fromindi.TAGS)


class _PortHandler:
    "Creates a connection and sends an receives to the indiserver port"

    def __init__(self, loop, rconn, indiserver):
        "Stores the argument values, and creates a collections.deque object"
        self.loop = loop
        self.rconn = rconn
        self.indiserver = indiserver
        self.to_indi = collections.deque(maxlen=100)

        # The to_indi dequeue has the right side filled from redis via toindi.SenderLoop
        # which monitors the traffic published to redis  and appends it to this deque
        # and the left side is sent to indiserver via this objects txtoindi method


    async def handle_data(self):
        "coroutine to create the connection and start the sender and receiver"
        # start by openning a connection
        reader, writer = await asyncio.open_connection(self.indiserver.host, self.indiserver.port)
        _message(self.rconn, f"Connected to {self.indiserver.host}:{self.indiserver.port}")
        await asyncio.gather(self.txtoindi(writer), self.rxfromindi(reader))


    async def txtoindi(self, writer):
        "Monitors to_indi deque and if it has data, pops it and uses writer to send it"
        while True:
            if self.to_indi:
                # Send the next message to the indiserver
                writer.write(self.to_indi.popleft())
                await writer.drain()
            else:
                # no message to send, do an async pause
                await asyncio.sleep(0.5)


    async def rxfromindi(self, reader):
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
                else:
                    # data does not start with a recognised tag, so ignore it
                    # and continue waiting for a valid message start
                    continue
                # set this data into the received message
                message = data
                # either further children of this tag are coming, or maybe its a single tag ending in "/>"
                if message.endswith(b'/>'):
                    # the message is complete, handle message here
                    # Run 'fromindi.receive_from_indiserver' in the default loop's executor:
                    try:
                        root = ET.fromstring(message.decode("utf-8"))
                    except Exception:
                        # possible malformed
                        message = b''
                        messagetagnumber = None
                        continue
                    result = await self.loop.run_in_executor(None, fromindi.receive_from_indiserver, message, root, self.rconn)
                    # result is None, or the device name if a defxxxx was received
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
                # Run 'fromindi.receive_from_indiserver' in the default loop's executor:
                try:
                    root = ET.fromstring(message.decode("utf-8"))
                except Exception:
                    # possible malformed
                    message = b''
                    messagetagnumber = None
                    continue
                result = await self.loop.run_in_executor(None, fromindi.receive_from_indiserver, message, root, self.rconn)
                # result is None, or the device name if a defxxxx was received
                # and start again, waiting for a new message
                message = b''
                messagetagnumber = None


def inditoredis(indiserver, redisserver, log_lengths={}, blob_folder=''):
    """Blocking call that provides the indiserver - redis conversion

    :param indiserver: Named Tuple providing the indiserver parameters
    :type indiserver: namedtuple
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

    print("inditoredis started")

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

    # Now create a loop to tx and rx to the indiserver port
    loop = asyncio.get_event_loop()
    indiconnection = _PortHandler(loop, rconn, indiserver)

    # Create a SenderLoop object, with the indiconnection.to_indi dequeue and redis connection
    senderloop = toindi.SenderLoop(indiconnection.to_indi, rconn, redisserver)
    # run senderloop - which is blocking, so run in its own thread
    run_toindi = threading.Thread(target=senderloop)
    # and start senderloop in its thread, this monitors data published via redis, and appends
    # it to indiconnection.to_indi, where it will be sent on to the indi connection
    run_toindi.start()

    while True:
        indiconnection.to_indi.clear()
        indiconnection.to_indi.append(b'<getProperties version="1.7" />')
        try:
            loop.run_until_complete(indiconnection.handle_data())
        except ConnectionRefusedError:
            _message(rconn, f"Connection refused on {indiserver.host}:{indiserver.port}, re-trying...")
            sleep(5)
        except asyncio.IncompleteReadError:
            _message(rconn, f"Connection failed on {indiserver.host}:{indiserver.port}, re-trying...")
            sleep(5)
        else:
            loop.close()
            break


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





