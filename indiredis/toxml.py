

###################
#
#  toxml
#
###################


"""Reads values from redis and converts them to indi xml which are then transmitted
   via a deque object."""


# if Client wants to learn all Devices and all their Properties
#  send <defProperties>
# if Client wants to change a Property value or state
#  set State to Busy
#  send <newXXX> with device, name and value
# if Client wants to query a Property’s target value or state
#  send <getTarValue> with device and name attributes


from time import sleep

import xml.etree.ElementTree as ET


_INDI_VERSION = "1.7"



class SenderLoop():

    "An instance of this object is callable, which when called, creates a blocking loop"

    def __init__(self, _TO_INDI, rconn, redisserver):
        """Set the _TO_INDI dequeue and redis connection"""
        self._TO_INDI = _TO_INDI
        self.rconn = rconn
        self.channel = redisserver.to_indi_channel


    def _handle(self, message):
        "date received from client, to be sent to indiserver"
        data = message['data'].decode("utf-8")
        et_data = None

        # convert data to an ET
        if data == "getProperties":
            et_data = ET.Element('getProperties', {"version":_INDI_VERSION})

        # and transmit it via the deque
        if et_data is not None:
            print(ET.tostring(et_data))
            self._TO_INDI.append(ET.tostring(et_data))


    def __call__(self):
        "Create the pubsub"
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





               
    

