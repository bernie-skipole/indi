#!/usr/bin/env python3

"""INDI driver to respond to getProperties

This script creates a socket listenning on localhost:7624 and acts as an indi driver.
It is used to create a response to a getProperties request, in which case it responds
with device IRTEST1 with a text vector containing two elements.

Normally this script is run from one terminal, and the indiredis client in another.
The client should then display the device and its two text elements"""

import os, sys
from time import sleep
from datetime import datetime
import xml.etree.ElementTree as ET

import asyncio

DEVICE = "IRTEST1"

# All xml data received from the client should be contained in one of the following tags
TAGS = (b'getProperties',
        b'enableBLOB',
        b'newTextVector',
        b'newNumberVector',
        b'newSwitchVector',
        b'newBLOBVector'
       )

# _STARTTAGS is a tuple of ( b'<getProperties', ...  ) data received will be tested to start with such a starttag

_STARTTAGS = tuple(b'<' + tag for tag in TAGS)

# _ENDTAGS is a tuple of ( b'</getProperties>', ...  ) data received will be tested to end with such an endtag

_ENDTAGS = tuple(b'</' + tag + b'>' for tag in TAGS)


async def handle_data(reader, writer):
    # received message
    message = b''
    messagetagnumber = None
    while True:
        # get blocks of data from the client
        try:
            data = await reader.readuntil(separator=b'>')
        except asyncio.LimitOverrunError:
            data = await reader.read(n=32000)
        except asyncio.IncompleteReadError:
            # connection possibly closed, abandon the message
            return
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
                # the message is complete, send a responce
                await txdata(writer, message)
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
            await txdata(writer, message)
            # and start again, waiting for a new message
            message = b''
            messagetagnumber = None


async def txdata(writer, message):
    "message is the message received, this coroutine now creates and sends a reply"
    print("Received: %r" % message)
    if (message == b'<getProperties version="1.7" />') or (message == b'<getProperties device="IRTEST1" version="1.7" />') or (message == b'<getProperties version="1.7" device="IRTEST1" />'):
        senddata = reply_getProperties()
    else:
        return
    print("Send: %r" % senddata)
    writer.write(senddata)
    await writer.drain()
    # append a system message
    systemmessage = _make_message("Message from test script irtest1.py")
    print("Send: %r" % systemmessage)
    writer.write(systemmessage)
    await writer.drain()
    # append a device message
    devicemessage = _make_message(f"Message from device {DEVICE}", DEVICE)
    print("Send: %r" % devicemessage)
    writer.write(devicemessage)
    await writer.drain()


def _make_message(message, device=None):
    "Print and return the message as an ElementTree string"
    sendmessage = ET.Element('message')
    if device:
        sendmessage.set("device", device)
    sendmessage.set("message", message)
    sendmessage.set("timestamp", datetime.utcnow().isoformat(timespec='seconds'))
    return ET.tostring(sendmessage)


def reply_getProperties():
    "Reply with properties for device with one textvector"
    senddata = ET.Element('defTextVector')
    senddata.set("device", DEVICE)
    senddata.set("name", "irtest1_text")
    senddata.set("label", "TextVector")
    senddata.set("state", "Ok")
    senddata.set("perm", "ro")
    senddata.set("timestamp", datetime.utcnow().isoformat(timespec='seconds'))
    # add text elements
    t1 = ET.SubElement(senddata, 'defText')
    t1.set("name", "irtest1_text_t1")
    t1.set("label", "TextElement T1")
    t1.text = "This is a test string for element T1"
    t2 = ET.SubElement(senddata, 'defText')
    t2.set("name", "irtest1_text_t2")
    t2.set("label", "TextElement T2")
    t2.text = "This is a second test string for element T2"
    return ET.tostring(senddata)


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle_data, '127.0.0.1', 7624, loop=loop)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()



        



