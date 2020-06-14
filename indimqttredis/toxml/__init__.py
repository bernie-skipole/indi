

###################
#
#  toxml
#
###################


"""Reads values from redis and converts them to indi xml which are then transmitted by a
   callable which should be registered by sender(sender_function)
   where sender_function is a function (or a callable) which can be called with sender_function(data)
   and which will transmit the data (a bytestring) to an indiserver."""


# if Client wants to learn all Devices and all their Properties
#  send <defProperties>
# if Client wants to change a Property value or state
#  set State to Busy
#  send <newXXX> with device, name and value
# if Client wants to query a Property’s target value or state
#  send <getTarValue> with device and name attributes


from time import sleep

import xml.etree.ElementTree as ET

_SEND = None         # will be set with the sender_function

_SEND_START = True   # Initially set to True to indicate startup

_INDI_VERSION = "1.7"


def sender(sender_function):
    "Register a sender function, which will be used to transmit binary data to indiserver"
    global _SEND
    _SEND = sender_function


def transmit_to_indiserver(data):
    """sends xml data to the indiserver, normally returns True, returns False if no sender function set
       data should be an ElementTree Element"""
    if _SEND is None:
        # sender has not yet been called to register a sender function
        return False
    # convert to binary data and send
    _SEND(ET.tostring(data))
    return True


def loop():
    "A blocking loop"
    global _SEND_START
    while _SEND_START:
        # initially wait for a few seconds to allow network connections to be made
        sleep(2)
        data = getProperties()
        if transmit_to_indiserver(data):
            _SEND_START = False
    while True:
        sleep(1)


def getProperties():
    "Creates a getProperties xml"
    return ET.Element('getProperties', {"version":_INDI_VERSION})





               
    

