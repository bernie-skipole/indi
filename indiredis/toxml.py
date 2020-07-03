

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

from datetime import datetime

from base64 import standard_b64decode, standard_b64encode

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

# If the command is getProperties, the indiredis package will always inset the indi Protocol Version 1.7 into
# the command, and so this value is not needed.

# publish message:   'getProperties:mykeystring'
# using list key "keyprefix:mykeystring" and value ["","",""]
# this is the  getProperties command, with no device specified, and therefore is a request for all device properties.
#                   
#
# NOTE: the indiredis package will delete the key and contents, once having read it.
#
#
# publish message:   'newTextVector:mykeystring'
# using list key "keyprefix:mykeystring" and list value [<devicename,<propertyname>,"",anotherkeystring, yetanotherkeystring]
#
# In this case no timestamp is given, so indiredis will insert one. Then indiredis will look up the two keys given
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
# So the list for the enableBLOB command will be of the form:
#
#  [<devicename,<propertyname>,"",<Never|Also|Only>]
#
# If propertyname is "", this command applies to all properties of the device.


_VECTORELEMENTS = { "newTextVector":"oneText",
                    "newNumberVector":"oneNumber",
                    "newSwitchVector":"oneSwitch",
                    "newBLOBVector":"oneBLOB" }


class SenderLoop():

    "An instance of this object is callable, which when called, creates a blocking loop"

    def __init__(self, _TO_INDI, rconn, redisserver):
        """Set the _TO_INDI dequeue and redis connection"""
        self._TO_INDI = _TO_INDI
        self.rconn = rconn
        self.channel = redisserver.to_indi_channel
        self.keyprefix = redisserver.keyprefix


    def _handle(self, message):
        "date received from client, to be sent to indiserver"
        data = message['data'].decode("utf-8")
        et_data = None

        # convert data to an ET
        if data.startswith("getProperties:"):
            et_data = _getProperties(self.rconn, self.keyprefix, data)
        if data.startswith("newBLOBVector:"):
            et_data = _newBLOBVector(self.rconn, self.keyprefix, data)
        elif data.startswith("new"):
            et_data = _newVector(self.rconn, self.keyprefix, data)
        else:
            return
        # and transmit it via the deque
        if et_data is not None:
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



def _getProperties(rconn, keyprefix, data):
    "Returns the xml, or None on failure"
    command = data.split(sep=":", maxsplit=1)
    if keyprefix:
        keystring =  keyprefix + ":" + command[1]
    else:
        keystring = command[1]
    if rconn.llen(keystring) != 3:
        return
    device = rconn.lpop(keystring).decode("utf-8")
    name = rconn.lpop(keystring).decode("utf-8")
    rconn.delete(keystring)
    if not device:
        return ET.Element('getProperties', {"version":_INDI_VERSION})
    if not name:
        return ET.Element('getProperties', {"version":_INDI_VERSION, "device":device})
    return ET.Element('getProperties', {"version":_INDI_VERSION, "device":device, "name":name})


def _newBLOBVector(rconn, keyprefix, data):
    "Returns the xml, or None on failure"
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
        # get value as a binary item
        value = attribs.pop(b'value', '')
        elementattribs = {att.decode("utf-8"):val.decode("utf-8") for att,val in attribs.items()}
        # get the element tag, for example, command "newTextVector" has element tag "oneText"
        # which is available by the _VECTORELEMENTS global dictionary
        xmlelement = ET.Element(_VECTORELEMENTS[command[0]], elementattribs)
        # value is a binary value, to be base64 encoded
        xmlelement.text = standard_b64encode(value)
        vector.append(xmlelement)
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
    return vector


               
    

