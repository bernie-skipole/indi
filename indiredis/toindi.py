

###################
#
#  toindi
#
###################


"""Reads xml strings published via redis and transmits
   via a deque object."""

from time import sleep

import xml.etree.ElementTree as ET


_INDI_VERSION = "1.7"


##
#
# all communications use the following method:
#
# client will publish via redis, on channel <to_indi_channel>, the xml message required
# Note: this leaves it to the client to format the correct xml according to the indi version 1.7
#
# This module subscribes to the <to_indi_channel>, and will inspect contents
#
# When a property state changes, according to the white paper:
#
#    When a Client sends a command to change a Property, the Client
#    shall henceforth consider the Property state to be Busy
#
# So this indredis package sets the state to Busy in the hash table 'attributes:<propertyname>:<devicename>'
# but does not publish a setXXXVector alert, as this is not from the indiserver


class SenderLoop():

    "An instance of this object is callable, which when called, creates a blocking loop"

    def __init__(self, sender, rconn, redisserver):
        """Set the sender object and a loop to read redis published messages from the client

           The sender object should have an append method, when data is appended to this object
           it should be sent to the indisserver.
           """
        self.sender = sender
        self.rconn = rconn
        self.channel = redisserver.to_indi_channel
        self.keyprefix = redisserver.keyprefix


    def _handle(self, message):
        "data published by the client, to be sent to indiserver"
        # an message is published by the client, giving the command
        data = message['data']
        root = ET.fromstring(data.decode("utf-8"))
        if root.tag == "newTextVector":
            self._set_busy(root)
        elif root.tag == "newNumberVector":
            self._set_busy(root)
        elif root.tag == "newSwitchVector":
            self._set_busy(root)
        elif root.tag == "newBLOBVector":
            self._set_busy(root)
        # and transmit the xml data via the sender object
        if data is not None:
            self.sender.append(data)


    def _set_busy(self, vector):
        "Set the property to Busy"
        attribs = vector.attrib
        # Required properties
        device = attribs.get("device")    # name of Device
        name = attribs.get("name")    # name of property
        if self.keyprefix:
            key = self.keyprefix + ":" + "devices"
        else:
            key = "devices"
        if not self.rconn.sismember(key, device):
            return
        # it is a known device
        if self.keyprefix:
            key = self.keyprefix + ":properties:" + device
        else:
            key = "properties:" + device
        if not self.rconn.sismember(key, name):
            return
        # it is a known property, set state to Busy
        if self.keyprefix:
            key = self.keyprefix + ":attributes:" + name + ":" + device
        else:
            key = "attributes:" + name + ":" + device
        self.rconn.hset(key, "state", "Busy")



    def __call__(self):
        "Create the redis pubsub loop"
        ps = self.rconn.pubsub(ignore_subscribe_messages=True)

        # subscribe with handler
        ps.subscribe(**{self.channel:self._handle})

        # any data received via the to_indi_channel will be sent to
        # the _handle method

        # blocks and listens to redis
        while True:
            message = ps.get_message()
            if message:
                print(message)
            sleep(0.1)






