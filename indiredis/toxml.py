

###################
#
#  toxml
#
###################


"""Reads values from redis and converts them to indi xml which are then transmitted
   via a deque object."""


from time import sleep

from datetime import datetime

from base64 import standard_b64encode

import xml.etree.ElementTree as ET


_INDI_VERSION = "1.7"


##
#
#
# all communications use the following method:
#
# client will set values into a redis List with key made from "keyprefix:mykeystring"
#
# The values in this list will be [device, propertyname, timestamp, elementstring1, elementstring2, ....]
# These act as the arguments to a command to be sent to indiserver.
# The first three items must always exist, but could be empty strings depending on the
# command to be sent. The following strings will be further redis keys which point to hashes representing
# the elements of the property to be set. The actual values 'mykeystring', 'elementstring1'... etc are
# arbitrary strings chosen by the client.
#
# client will then publish, on channel <to_indi_channel>, the message "<commandname>:<mykeystring>"
#
# The indiredis package subscribes to the <to_indi_channel>, and will then lookup the "keyprefix:mykeystring" list,
# and interpret it as in the following examples.

# If the command is getProperties, the indiredis package will always insert the indi Protocol Version 1.7 into
# the command, and so this value is not needed.

# published message received:   'getProperties:mykeystring'
# using list key "keyprefix:mykeystring" and value ["","",""]
# this is the  getProperties command, with no device specified, and therefore is a request for all device properties.
#                   
#
# NOTE: the indiredis package will delete the keys and contents, once having read it.
#
#
# published message redeived:   'newTextVector:mykeystring'
# using list key "keyprefix:mykeystring" and list value [<devicename,<propertyname>,"",anotherkeystring, yetanotherkeystring]
#
# In this case no timestamp is given, so indiredis will insert one. Then indiredis will look up the two keys given to read
# two text elements
#
# key "keyprefix:anotherkeystring" should contain a hash table.
# similarly key "keyprefix:yetanotherkeystring" should contain a hash table.
#
# In this case, each hash table will correspond to the oneText element and be of the form:
# {name:<elementname>, value:<elementvalue>}
#
# generally the hash table will give the attributes of the element, with the attribute 'value' being set as the element's value.
#
# There is one exception to this rule. The enableBLOB command does not include any elements, but only one string of Never|Also|Only
# So the list for the enableBLOB command does not contain element keys, but will be of the form:
#
#  [<devicename,<propertyname>,"",<Never|Also|Only>]
#
# If propertyname is "", this command applies to all properties of the device.
#
#
#
# When a property state changes, according to the white paper:
#
#    When a Client sends a command to change a Property, the Client
#    shall henceforth consider the Property state to be Busy
#
# So this indredis package sets the state to Busy in the hash table 'attributes:<propertyname>:<devicename>'
# but does not publish a setXXXVector alert, as this is not from the indiserver


_VECTORELEMENTS = { "newTextVector":"oneText",
                    "newNumberVector":"oneNumber",
                    "newSwitchVector":"oneSwitch",
                    "newBLOBVector":"oneBLOB" }


class SenderLoop():

    "An instance of this object is callable, which when called, creates a blocking loop"

    def __init__(self, sender, rconn, redisserver):
        """Set the sender object and a loop to read redis published alerts from the client

           The sender object should have an append method, when data is appended to this object
           it should be sent to the indisserver.
           """
        self.sender = sender
        self.rconn = rconn
        self.channel = redisserver.to_indi_channel
        self.keyprefix = redisserver.keyprefix


    def _handle(self, message):
        "data published by the client, to be sent to indiserver"
        # an alert is published by the client, giving the command
        # and a redis key string pointing to the data to be sent 
        data = message['data'].decode("utf-8")
        et_data = None
        # get the details from redis key stores and convert to xml 
        if data.startswith("getProperties:"):
            et_data = _getProperties(self.rconn, self.keyprefix, data)
        elif data.startswith("enableBLOB:"):
            et_data = _enableBLOB(self.rconn, self.keyprefix, data)
        elif data.startswith("newBLOBVector:"):
            et_data = _newBLOBVector(self.rconn, self.keyprefix, data)
        elif data.startswith("new"):
            et_data = _newVector(self.rconn, self.keyprefix, data)
        else:
            # the published alert from the client is not recognised
            return
        # and transmit the xml data via the sender object
        if et_data is not None:
            self.sender.append(ET.tostring(et_data))


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


############################################################
# Different commands have to be treated in different ways,
# the _handle method calls these functions which are used to
# read redis stores, and fill the xml structure
#############################################################


def _getProperties(rconn, keyprefix, data):
    "Returns the xml for the getProperties command, or None on failure"
    command = data.split(sep=":", maxsplit=1)
    # get the store key
    if keyprefix:
        keystring =  keyprefix + ":" + command[1]
    else:
        keystring = command[1]
    # getProperties should only have device, property name and optionally timestamp
    # timestamp is unused, but allowed so a uniform store is used across commands
    if rconn.llen(keystring) < 2:
        return
    device = rconn.lpop(keystring).decode("utf-8")
    name = rconn.lpop(keystring).decode("utf-8")
    rconn.delete(keystring)
    if not device:
        return ET.Element('getProperties', {"version":_INDI_VERSION})
    if not name:
        return ET.Element('getProperties', {"version":_INDI_VERSION, "device":device})
    return ET.Element('getProperties', {"version":_INDI_VERSION, "device":device, "name":name})


def _enableBLOB(rconn, keyprefix, data):
    "Returns the xml for the enableBLOB command, or None on failure"
    command = data.split(sep=":", maxsplit=1)
    if keyprefix:
        keystring =  keyprefix + ":" + command[1]
    else:
        keystring = command[1]
    if rconn.llen(keystring) != 4:
        return
    device = rconn.lpop(keystring).decode("utf-8")
    name = rconn.lpop(keystring).decode("utf-8")
    timestamp = rconn.lpop(keystring) # unused
    value = rconn.lpop(keystring).decode("utf-8")
    rconn.delete(keystring)
    if not device:
        return
    if value not in ["Never", "Also", "Only"]:
        return
    if not name:
        vector = ET.Element('enableBLOB', {"device":device})
    else:
        vector = ET.Element('enableBLOB', {"device":device, "name":name})
    vector.text = value
    return vector


def _newBLOBVector(rconn, keyprefix, data):
    "Returns the xml for the newBLOBVector command, or None on failure"
    command = data.split(sep=":", maxsplit=1)
    # command[0] is newBLOBVector
    # command[1] is the key string provided by the client
    if keyprefix:
        keystring =  keyprefix + ":" + command[1]
    else:
        keystring = command[1]
    if rconn.llen(keystring) < 4:
        return
    device = rconn.lpop(keystring).decode("utf-8")
    if not device:
        return
    name = rconn.lpop(keystring).decode("utf-8")
    if not name:
        return
    timestamp = rconn.lpop(keystring).decode("utf-8")
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()
    # get the element keys
    elementkeys = []
    while True:
        key = rconn.lpop(keystring)
        if key is None:
            break
        elementkeys.append(key.decode("utf-8"))
    rconn.delete(keystring)
    vector = ET.Element("newBLOBVector", {"device":device, "name":name, "timestamp":timestamp})
    for key in elementkeys:
        if keyprefix:
            ekey = keyprefix + ":" + key
        else:
            ekey = key
        attribs = rconn.hgetall(ekey)
        if attribs is None:
            continue
        rconn.delete(ekey)
        # get value as a binary item
        value = attribs.pop(b'value', b'')
        elementattribs = {att.decode("utf-8"):val.decode("utf-8") for att,val in attribs.items()}
        xmlelement = ET.Element("oneBLOB", elementattribs)
        # value is a binary value, to be base64 encoded
        xmlelement.text = standard_b64encode(value)
        vector.append(xmlelement)
    _set_busy(rconn, keyprefix, device, name)
    return vector


def _newVector(rconn, keyprefix, data):
    "Returns the xml, or None on failure"
    command = data.split(sep=":", maxsplit=1)
    # command[0] is one of the newVector commands such as newTextVector
    # command[1] is the key string provided by the client
    if command[0] not in _VECTORELEMENTS:
        return
    if keyprefix:
        keystring =  keyprefix + ":" + command[1]
    else:
        keystring = command[1]
    if rconn.llen(keystring) < 4:
        return
    device = rconn.lpop(keystring).decode("utf-8")
    if not device:
        return
    name = rconn.lpop(keystring).decode("utf-8")
    if not name:
        return
    timestamp = rconn.lpop(keystring).decode("utf-8")
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()
    # get the element keys
    elementkeys = []
    while True:
        key = rconn.lpop(keystring)
        if key is None:
            break
        elementkeys.append(key.decode("utf-8"))
    rconn.delete(keystring)
    vector = ET.Element(command[0], {"device":device, "name":name, "timestamp":timestamp})
    for key in elementkeys:
        if keyprefix:
            ekey = keyprefix + ":" + key
        else:
            ekey = key
        attribs = rconn.hgetall(ekey)
        if attribs is None:
            continue
        rconn.delete(ekey)
        elementattribs = {att.decode("utf-8"):val.decode("utf-8") for att,val in attribs.items()}
        value = elementattribs.pop('value', '')
        # get the element tag, for example, command "newTextVector" has element tag "oneText"
        # which is available by the _VECTORELEMENTS global dictionary
        xmlelement = ET.Element(_VECTORELEMENTS[command[0]], elementattribs)
        xmlelement.text = value
        vector.append(xmlelement)
    _set_busy(rconn, keyprefix, device, name)
    return vector


#   one key : set
#   'devices' - set of device names   ('devices' is a literal string)

#   multiple keys : sets
#   'properties:<devicename>' - set of property names for the device ('properties' is a literal string
#                                                                     <devicename> is an actual device name)

#   multiple keys : hash tables ( python dictionaries )
#   'attributes:<propertyname>:<devicename>' - dictionary of attributes for the property ('attributes' is a literal string
#                                                                                         <propertyname> is an actual property name
#                                                                                         <devicename> is an actual device name

def _set_busy(rconn, keyprefix, device, name):
    "Set a property state to Busy"
    if keyprefix:
        key = keyprefix + ":" + "devices"
    else:
        key = "devices"
    if not rconn.sismember(key, device):
        return
    # it is a known device
    if keyprefix:
        key = keyprefix + ":properties:" + device
    else:
        key = "properties:" + device
    if not rconn.sismember(key, name):
        return
    # it is a known property, set state to Busy
    if keyprefix:
        key = keyprefix + ":attributes:" + name + ":" + device
    else:
        key = "attributes:" + name + ":" + device
    rconn.hset(key, "state", "Busy")





