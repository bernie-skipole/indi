


import sys, collections, threading, asyncio

from time import sleep

from . import toindi, fromindi, tools

REDIS_AVAILABLE = True
try:
    import redis
except:
    REDIS_AVAILABLE = False

# The _TO_INDI dequeue has the right side filled from redis and the left side
# sent to indiserver. Limit length to five items - an arbitrary setting

_TO_INDI = collections.deque(maxlen=5)


# All xml data received should be contained in one of the following tags
_TAGS = (b'defTextVector',
         b'defNumberVector',
         b'defSwitchVector',
         b'defLightVector',
         b'defBLOBVector',
         b'message',
         b'delProperty',
         b'setTextVector',
         b'setNumberVector',
         b'setSwitchVector',
         b'setLightVector',
         b'setBLOBVector'
        )

_STARTTAGS = tuple(b'<' + tag for tag in _TAGS)

# _STARTTAGS is a tuple of ( b'<defTextVector', ...  ) data received will be tested to start with such a starttag

_ENDTAGS = tuple(b'</' + tag + b'>' for tag in _TAGS)

# _ENDTAGS is a tuple of ( b'</defTextVector>', ...  ) data received will be tested to end with such an endtag


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
        data = await reader.readuntil(separator=b'>')
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
    reader, writer = await asyncio.open_connection(indiserver.host, indiserver.port)
    sent = _txtoindi(writer)
    received = _rxfromindi(reader, loop, rconn)
    await asyncio.gather(sent, received)


def inditoredis(indiserver, redisserver):
    "Blocking call that provides the indiserver - redis conversion"
    global _TO_INDI

    if not REDIS_AVAILABLE:
        print("Error - Unable to import the Python redis package")
        sys.exit(1)

    print("inditoredis started")

    # wait two seconds before starting, to give servers
    # time to start up
    sleep(2)

    # set up the redis server
    rconn = _open_redis(redisserver)
    # set the prefix to use for redis keys
    fromindi.setup_redis(redisserver.keyprefix, redisserver.to_indi_channel, redisserver.from_indi_channel)

    # on startup, clear all redis keys
    tools.clearredis(rconn, redisserver)

    # Create a SenderLoop object, with the _TO_INDI dequeue and redis connection
    senderloop = toindi.SenderLoop(_TO_INDI, rconn, redisserver)
    # run senderloop - which is blocking, so run in its own thread
    run_toindi = threading.Thread(target=senderloop)
    # and start senderloop in its thread
    run_toindi.start()
    # the senderloop will place data to transmit to indiserver in the _TO_INDI dequeue

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_indiconnection(loop, rconn, indiserver))
    loop.close()


