
"""Defines blocking function inditoredis:
   
       Receives XML data from indiserver on port 7624 and stores in redis.
       Reads data published via redis, and outputs to port 7624 and indiserver.

   """

import os, sys, collections, threading, asyncio, pathlib

from time import sleep

from datetime import datetime

from . import toindi, fromindi, tools

REDIS_AVAILABLE = True
try:
    import redis
except:
    REDIS_AVAILABLE = False

# The _TO_INDI dequeue has the right side filled from redis and the left side
# sent to indiserver. Limit length to five items - an arbitrary setting

_TO_INDI = collections.deque(maxlen=5)

# _STARTTAGS is a tuple of ( b'<defTextVector', ...  ) data received will be tested to start with such a starttag

_STARTTAGS = tuple(b'<' + tag for tag in fromindi.TAGS)

# _ENDTAGS is a tuple of ( b'</defTextVector>', ...  ) data received will be tested to end with such an endtag

_ENDTAGS = tuple(b'</' + tag + b'>' for tag in fromindi.TAGS)


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


async def _rxfromindi(reader, loop, rconn):
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
            if messagetagnumber is None:
                # data does not start with a recognised tag, so ignore it
                # and continue waiting for a valid message start
                continue
            # set this data into the received message
            message = data
            # either further children of this tag are coming, or maybe its a single tag ending in "/>"
            if message.endswith(b'/>'):
                # the message is complete, handle message here
                # Run 'fromindi.receive_from_indiserver' in the default loop's executor:
                result = await loop.run_in_executor(None, fromindi.receive_from_indiserver, message, rconn)
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
            result = await loop.run_in_executor(None, fromindi.receive_from_indiserver, message, rconn)
            # and start again, waiting for a new message
            message = b''
            messagetagnumber = None


async def _indiconnection(loop, rconn, indiserver):
    "coroutine to create the connection and start the sender and receiver"
    # start by sending a getproperties
    reader, writer = await asyncio.open_connection(indiserver.host, indiserver.port)
    _message(rconn, f"Connected to {indiserver.host}:{indiserver.port}")
    sent = _txtoindi(writer)
    received = _rxfromindi(reader, loop, rconn)
    await asyncio.gather(sent, received)


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

    global _TO_INDI

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

    # Create a SenderLoop object, with the _TO_INDI dequeue and redis connection
    senderloop = toindi.SenderLoop(_TO_INDI, rconn, redisserver)
    # run senderloop - which is blocking, so run in its own thread
    run_toindi = threading.Thread(target=senderloop)
    # and start senderloop in its thread
    run_toindi.start()
    # the senderloop will place data to transmit to indiserver in the _TO_INDI dequeue
    # Now create a loop to tx and rx to the indiserver port
    loop = asyncio.get_event_loop()
    while True:
        _TO_INDI.clear()
        _TO_INDI.append(b'<getProperties version="1.7" />')
        try:
            loop.run_until_complete(_indiconnection(loop, rconn, indiserver))
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





