

###################
#
#  toindi
#
###################


"""Reads xml strings published via redis and transmits
   via a deque object."""

from time import sleep

from datetime import datetime

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

# If enableBLOB is sent, the Busy flag is not set (as it is not clear if this is a 'property')
# however the redis property blobs attribute is set to Enabled or Disabled



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
            sleep(0.1)


    def _handle(self, message):
        "data published by the client, to be sent to indiserver"
        # a message is published by the client, giving the command
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
        elif root.tag == "enableBLOB":
            self._set_blob_state(root)
        elif root.tag == "getProperties":
            self._set_timestamp(root)
        # and transmit the xml data via the sender object
        if data is not None:
            self.sender.append(data)


    def _set_busy(self, vector):
        "Set the property to Busy"
        # Required properties
        device = vector.get("device")    # name of Device
        name = vector.get("name")    # name of property
        if (device is None) or (name is None):
            return
        if self.keyprefix:
            key = self.keyprefix + "devices"
        else:
            key = "devices"
        if not self.rconn.sismember(key, device):
            return
        # it is a known device
        if self.keyprefix:
            key = self.keyprefix + "properties:" + device
        else:
            key = "properties:" + device
        if not self.rconn.sismember(key, name):
            return
        # it is a known property, set state to Busy
        if self.keyprefix:
            key = self.keyprefix + "attributes:" + name + ":" + device
        else:
            key = "attributes:" + name + ":" + device
        self.rconn.hset(key, "state", "Busy")


    def _set_blob_state(self, vector):
        "Sets blobs enabled or disabled"
        # if instruction is Never, this disables the property blobs attribute
        # however Also and Only enables it
        device = vector.get("device")    # name of Device
        if device is None:
            return
        instruction = vector.text
        if instruction not in ("Never", "Also", "Only"):
            return
        name = vector.get("name")    # name of property, could be None
        if self.keyprefix:
            key = self.keyprefix + "devices"
        else:
            key = "devices"
        if not self.rconn.sismember(key, device):
            # device not recognised
            return
        # it is a known device, get all properties
        if self.keyprefix:
            key = self.keyprefix + "properties:" + device
        else:
            key = "properties:" + device
        propertyset = self.rconn.smembers(key)
        if not propertyset:
            return
        propertylist = list(p.decode("utf-8") for p in propertyset)
        if name is None:
            # set blob status in all blob vectors
            for propertyname in propertylist:
                if self.keyprefix:
                    key = self.keyprefix + "attributes:" + propertyname + ":" + device
                else:
                    key = "attributes:" + propertyname + ":" + device
                blob_status = self.rconn.hget(key, "blobs")
                if blob_status is None:
                    # not a blobvector
                    continue
                if instruction == "Never":
                    self.rconn.hset(key, "blobs", "Disabled")
                else:
                    self.rconn.hset(key, "blobs", "Enabled")
        elif name in propertylist:
            # set blob status for just this property
            if self.keyprefix:
                key = self.keyprefix + "attributes:" + name + ":" + device
            else:
                key = "attributes:" + name + ":" + device
            if instruction == "Never":
                self.rconn.hset(key, "blobs", "Disabled")
            else:
                self.rconn.hset(key, "blobs", "Enabled")


    def _set_timestamp(self, vector):
        "Set the redis timestamp keys when a getvector is sent"
        device = vector.get("device")    # name of Device
        name = vector.get("name")    # name of property
        timestamp = datetime.utcnow().isoformat(timespec='seconds')
        if device is None:
            # data is a general getProperties set the timestamp in redis
            if self.keyprefix:
                key = self.keyprefix + "getProperties"
            else:
                key = "getProperties"
        elif name is None:
            # data is a getProperties for a device
            if self.keyprefix:
                key = self.keyprefix + "getProperties:device:" + device
            else:
                key = "getProperties:device:" + device
        else:
            # data is a getProperties for a device and property name
            if self.keyprefix:
                key = self.keyprefix + "getProperties:property:" + name + ":" + device
            else:
                key = "getProperties:property:" + name + ":" + device
        self.rconn.set(key, timestamp)

