

"""This is a set of Python functions which read, and publish to your redis server.
You may find them useful when creating a client gui, if your gui is Python based.

Functions are provided which open a redis connection, and return lists of devices,
properties, elements etc., further functions create xml elements and publish them
which transmits the values on to indiserver and hence the attached instruments.

These functions take the namedtuple redisserver as an argument and apply the key
prefix as defined in the tuple to the redis keys.

indiserver must be running, and inditoredis, typically in other processes. These
functions can then be imported into your own GUI clent as a convenient way of
accessing redis.

Your script could start with::

    from indiredis import redis_server, tools

    redisserver = redis_server(host='localhost', port=6379)
    rconn = tools.open_redis(redisserver)

and then using rconn and redisserver you could call upon the functions provided here.

Where a timestamp is specified, unless otherwise stated, it will be a string according to the INDI v1.7 white paper which describes it as::

    A timeValue shall be specified in UTC in the form YYYY-MM-DDTHH:MM:SS.S. The final decimal and subsequent
    fractional seconds are optional and may be specified to whatever precision is deemed necessary by the transmitting entity.
    This format is in general accord with ISO 86015 and the Complete forms defined in W3C Note "Date and Time Formats"

"""


import xml.etree.ElementTree as ET

from datetime import datetime

from base64 import standard_b64encode

import re, json, math

REDIS_AVAILABLE = True
try:
    import redis
except:
    REDIS_AVAILABLE = False


def _key(redisserver, *keys):
    "Add the prefix to keys, delimit keys with :"
    # example - if keys are 'device', 'property' this will result in a key of
    # 'keyprefixdevice:property'
    return redisserver.keyprefix + ":".join(keys)


def open_redis(redisserver):
    """Opens a redis connection, return None on failure

    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :return: A redis connection, or None on failure
    :rtype: redis.client.Redis
    """
    if not REDIS_AVAILABLE:
        return
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


def getproperties_timestamp(rconn, redisserver, name="", device=""):
    """Return the timestamp string when the last getProperties command was sent
       by the client, with the given optional device and property name
       Returns None if not available

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :param name: Optional property name
    :type name: String
    :param device: Optional device name
    :type device: String
    :return: A string of timestamp
    :rtype: String
    """
    if not device:
        # general
        key = _key(redisserver, "getProperties")
    elif not name:
        # device only
        key = _key(redisserver, "getProperties", "device", device)
    else:
        # device and property
        key = _key(redisserver, "getProperties", "property", name, device)
    try:
        timestamp = rconn.get(key)
    except:
        return
    if timestamp is None:
        return
    return timestamp.decode("utf-8")


def last_message(rconn, redisserver, device=""):
    """Return the last message or None if not available

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :param device: If given, the device to which the message pertains.
    :type device: String
    :return: A string of timestamp space message text.
    :rtype: String
    """
    try:
        if device:
            mkey = _key(redisserver, "devicemessages", device)
        else:
            mkey = _key(redisserver, "messages")
        message = rconn.get(mkey)
    except:
       rconn.delete(mkey)
       message = None
    if message is None:
        return
    return message.decode("utf-8")


def devices(rconn, redisserver):
    """Returns a list of devices.
    
    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :return: A list of device name strings, sorted in name order
    :rtype: List
    """
    devicekey = _key(redisserver, "devices")
    deviceset = rconn.smembers(devicekey)
    if not deviceset:
        return []
    devicelist = list(d.decode("utf-8") for d in deviceset)
    devicelist.sort()
    return devicelist


def properties(rconn, redisserver, device):
    """Returns a list of property names for the given device.

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :param device: The device name
    :type device: String
    :return: A list of property name strings, sorted in name order
    :rtype: List
    """
    propertykey = _key(redisserver, "properties", device)
    propertyset = rconn.smembers(propertykey)
    if not propertyset:
        return []
    propertylist = list(p.decode("utf-8") for p in propertyset)
    propertylist.sort()
    return propertylist


def elements(rconn, redisserver, name, device):
    """Returns a list of element names for the given property and device
    sorted by element names

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :param name: The property name
    :type name: String
    :param device: The device name
    :type device: String
    :return: A list of element name strings, sorted in name order
    :rtype: List
    """
    elementkey = _key(redisserver, "elements", name, device)
    elementset = rconn.smembers(elementkey)
    if not elementset:
        return []
    elementlist = list(e.decode("utf-8") for e in elementset)
    elementlist.sort()
    return elementlist


def attributes_dict(rconn, redisserver, name, device):
    """Returns a dictionary of attributes for the given property and device

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :param name: The property name
    :type name: String
    :param device: The device name
    :type device: String
    :return: A dictionary of property attributes
    :rtype: Dict
    """
    attkey = _key(redisserver, "attributes", name, device)
    attdict = rconn.hgetall(attkey)
    if not attdict:
        return {}
    return {k.decode("utf-8"):v.decode("utf-8") for k,v in attdict.items()}


def elements_dict(rconn, redisserver, elementname, name, device):
    """Returns a dictionary of element attributes for the given element, property and device

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :param elementname: The element name
    :type elementname: String
    :param name: The property name
    :type name: String
    :param device: The device name
    :type device: String
    :return: A dictionary of element attributes
    :rtype: Dict
    """
    elkey = _key(redisserver, "elementattributes", elementname, name, device)
    eldict = rconn.hgetall(elkey)
    if not eldict:
        return {}
    result = {}
    for k,v in eldict.items():
        key = k.decode("utf-8")
        value = v.decode("utf-8")
        if key.startswith("float_"):
            value = float(value)
        result[key] = value
    return result


# Two functions to help sort elements by the element label
# regardless of label being in text or numeric form

def _int_or_string(part):
    "Return integer or string"
    return int(part) if part.isdigit() else part

def _split_element_labels(element):
    "Splits the element label into text and integer parts"
    return [ _int_or_string(part) for part in re.split(r'(\d+)', element["label"]) ]

## use the above with
## newlist = sorted(oldlist, key=_split_element_labels)
## where the lists are lists of element dictionaries


def property_elements(rconn, redisserver, name, device):
    """Returns a list of dictionaries of element attributes for the given property and device
    each dictionary will be set in the list in order of label

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :param name: The property name
    :type name: String
    :param device: The device name
    :type device: String
    :return: A list of element attributes dictionaries.
    :rtype: List
    """
    element_name_list = elements(rconn, redisserver, name, device)
    if not element_name_list:
        return []
    element_dictionary_list = list( elements_dict(rconn, redisserver, elementname, name, device) for elementname in element_name_list )
    # sort element_dictionary_list by label
    element_dictionary_list.sort(key=_split_element_labels)
    return element_dictionary_list


def logs(rconn, redisserver, number, *keys):
    """Return the number of logs as [[timestamp,data], ...] or empty list if none available
    where timestamp is the time at which data is received, and data is a json string
    of the data logged.

    The keys positional arguments define where the logs are sourced, so if just the literal string "devices"
    the logs will come from "logdata:devices", if arguments are 'elementattributes', elementname, propertyname,
    devicename where elementattributes is a literal string and the other values are the actual names, then logs
    will come from redis store "logdata:elementattributes:<elementname>:<propertyname>:<devicename>"

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :param number: The number of logs to return
    :type number: Integer
    :param keys: Defines which redis key is the source of the logs.
    :type keys: Positional arguments
    :return: A list of lists, inner lists being [timestamp string, json data string]
    :rtype: List
    """
    if number < 1:
        return []
    logkey = _key(redisserver, "logdata", *keys)
    if number == 1:
        logentry = rconn.lindex(logkey, 0)
        if logentry is None:
            return []
        logtime, logdata = logentry.decode("utf-8").split(" ", maxsplit=1)
        logdata = json.loads(logdata)
        return [[logtime,logdata]]
    logs = rconn.lrange(logkey, 0, number-1)
    if logs is None:
        return []
    nlogs = []
    for logentry in logs:
        logtime, logdata = logentry.decode("utf-8").split(" ", maxsplit=1)
        logdata = json.loads(logdata)
        nlogs.append([logtime,logdata])
    return nlogs


# The following functions create the XML elements, and uses redis to publish the XML on the to_indi_channel.
# This is picked up by the inditoredis process (which subscribes to the to_indi_channel), and
# which then transmits the xml on to indisserver.

def getProperties(rconn, redisserver, name="", device=""):
    """Publishes a getProperties request on the to_indi_channel. If device and name
    are not specified this is a general request for all devices and properties.

    If device only is given then this is a request for all properties of that device, if
    device and name is given, this requests an update for that property of the given device.
    If name is given, device must also be given.

    Return the xml string sent, or None on failure.

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :param name: If given, should be the property name.
    :type name: String
    :param device: If given, should be the device name.
    :type device: String
    :return: A string of the xml published, or None on failure
    :rtype: String
    """
    gP = ET.Element('getProperties')
    gP.set("version", "1.7")
    if device:
        gP.set("device", device)
        if name:
            gP.set("name", name)
    etstring = ET.tostring(gP)
    try:
        rconn.publish(redisserver.to_indi_channel, etstring)
    except:
        etstring = None
    return etstring


def newswitchvector(rconn, redisserver, name, device, values, timestamp=None):
    """Sends a newSwitchVector request, returns the xml string sent, or None on failure.
    Values should be a dictionary of element name:state where state is On or Off.
    Timestamp should be a datetime object, if None the current utc datetime will be used.

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :param name: The property name
    :type name: String
    :param device: The device name
    :type device: String
    :param values: Dictionary of {element name:state, ... }
    :type values: Dict
    :param timestamp: A datetime.datetime object or None
    :type timestamp: datetime.datetime
    :return:  A string of the xml published, or None on failure
    :rtype: String
    """
    nsv = ET.Element('newSwitchVector')
    nsv.set("device", device)
    nsv.set("name", name)
    if timestamp is None:
        nsv.set("timestamp", datetime.utcnow().isoformat(sep='T'))
    else:
        nsv.set("timestamp", timestamp.isoformat(sep='T'))
    # set the switch elements 
    for ename, state in values.items():
        if (state != "On") and (state != "Off"):
            # invalid state
            return
        os = ET.Element('oneSwitch')
        os.set("name", ename)
        os.text = state
        nsv.append(os)
    nsvstring = ET.tostring(nsv)
    try:
        rconn.publish(redisserver.to_indi_channel, nsvstring)
    except:
        nsvstring = None
    return nsvstring


# The Client must send all members of Number and Text vectors,
# or may send just the members that change for other types.

def newtextvector(rconn, redisserver, name, device, values, timestamp=None):
    """Sends a newTextVector request, returns the xml string sent, or None on failure.
    Values should be a dictionary of element names : text values.
    Timestamp should be a datetime object, if None the current utc datetime will be used.

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :param name: The property name
    :type name: String
    :param device: The device name
    :type device: String
    :param values: Dictionary of {element name:new text, ... }
    :type values: Dict
    :param timestamp: A datetime.datetime object or None
    :type timestamp: datetime.datetime
    :return:  A string of the xml published, or None on failure
    :rtype: String
    """
    # get current values
    elementlist = elements(rconn, redisserver, name, device)
    if not elementlist:
        return
    ntv = ET.Element('newTextVector')
    ntv.set("device", device)
    ntv.set("name", name)
    if timestamp is None:
        ntv.set("timestamp", datetime.utcnow().isoformat(sep='T'))
    else:
        ntv.set("timestamp", timestamp.isoformat(sep='T'))
    # All elements must be sent
    # for any element not given in values, add to ntv
    for ename in elementlist:
        if ename in values:
            continue
        edict = elements_dict(rconn, redisserver, ename, name, device)
        ot = ET.Element('oneText')
        ot.set("name", ename)
        ot.text = edict['value']
        ntv.append(ot)
    # for all those elements given in values, add to ntv
    for ename, text in values.items():
        ot = ET.Element('oneText')
        ot.set("name", ename)
        ot.text = text
        ntv.append(ot)
    ntvstring = ET.tostring(ntv)
    try:
        rconn.publish(redisserver.to_indi_channel, ntvstring)
    except:
        ntvstring = None
    return ntvstring


def newnumbervector(rconn, redisserver, name, device, values, timestamp=None):
    """Sends a newNumberVector request, returns the xml string sent, or None on failure.
    Values should be a dictionary of element names : numeric values.
    Timestamp should be a datetime object, if None the current utc datetime will be used.

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :param name: The property name
    :type name: String
    :param device: The device name
    :type device: String
    :param values: Dictionary of {element name:new number, ... }
    :type values: Dict
    :param timestamp: A datetime.datetime object or None
    :type timestamp: datetime.datetime
    :return:  A string of the xml published, or None on failure
    :rtype: String
    """
    # get current values
    elementlist = elements(rconn, redisserver, name, device)
    if not elementlist:
        return
    nnv = ET.Element('newNumberVector')
    nnv.set("device", device)
    nnv.set("name", name)
    if timestamp is None:
        nnv.set("timestamp", datetime.utcnow().isoformat(sep='T'))
    else:
        nnv.set("timestamp", timestamp.isoformat(sep='T'))
    # All elements must be sent
    # for any element not given in values, add to nnv
    for ename in elementlist:
        if ename in values:
            continue
        edict = elements_dict(rconn, redisserver, ename, name, device)
        ot = ET.Element('oneNumber')
        ot.set("name", ename)
        ot.text = edict['value']
        nnv.append(ot)
    # for all those elements given in values, add to nnv
    for ename, number in values.items():
        ot = ET.Element('oneNumber')
        ot.set("name", ename)
        ot.text = number
        nnv.append(ot)
    nnvstring = ET.tostring(nnv)
    try:
        rconn.publish(redisserver.to_indi_channel, nnvstring)
    except:
        nnvstring = None
    return nnvstring



def newblobvector(rconn, redisserver, name, device, values, timestamp=None):
    """Sends a newBLOBVector request, returns the xml string sent, or None on failure.
    Values should be a list of dictionaries, each dictionary with key of name, size, format, value.
    The name key should contain the element name,
    size: number of bytes in the uncompressed BLOB,
    format: a file suffix,
    value: the data as bytes, but not base64 encoded, this function will do that.
    Timestamp should be a datetime object, if None the current utc datetime will be used.

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :param name: The property name
    :type name: String
    :param device: The device name
    :type device: String
    :param values: List of element dictionaries
    :type values: List
    :param timestamp: A datetime.datetime object or None
    :type timestamp: datetime.datetime
    :return:  A string of the xml published, or None on failure
    :rtype: String
    """
    nbv = ET.Element('newBLOBVector')
    nbv.set("device", device)
    nbv.set("name", name)
    if timestamp is None:
        nbv.set("timestamp", datetime.utcnow().isoformat(sep='T'))
    else:
        nbv.set("timestamp", timestamp.isoformat(sep='T'))
    # for the elements given in values, add to nbv
    try:
        for element in values:
            ob = ET.Element('oneBLOB')
            ob.set("name", element['name'])
            ob.set("size", str(element['size']))
            ob.set("format", element['format'])
            ob.text = standard_b64encode(element['value']).decode('ascii')
            nbv.append(ob)
        nbvstring = ET.tostring(nbv)
        rconn.publish(redisserver.to_indi_channel, nbvstring)
    except:
        nbvstring = None
    return nbvstring



# Command to control whether setBLOBs should be sent to this channel from a given Device. They can
# be turned off completely by setting Never (the default), allowed to be intermixed with other INDI
# commands by setting Also or made the only command by setting Only.
# <!ELEMENT enableBLOB %BLOBenable >
# <!ATTLIST enableBLOB
# device %nameValue; #REQUIRED        name of Device
# name %nameValue; #IMPLIED           name of BLOB Property, or all if absent

# BLOBenable is one of Never|Also|Only


def enableblob(rconn, redisserver, name, device, instruction):
    """Sends an enableBLOB instruction, returns the xml string sent, or None on failure,
    instruction should be one of Never, Also or Only.

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    :param name: Property name, if empty applies to all properties
    :type name: String
    :param device: The device name
    :type device: String
    :param instruction: One of Never, Also or Only
    :type instruction: String
    :return:  A string of the xml published, or None on failure
    :rtype: String
    """
    eb = ET.Element('enableBLOB')
    eb.set("device", device)
    if name:
        eb.set("name", name)
    instruction = instruction.lower().strip()
    if instruction == "never":
        eb.text = "Never"
    elif instruction == "also":
        eb.text = "Also"
    elif instruction == "only":
        eb.text = "Only"
    else:
        return
    ebstring = ET.tostring(eb)
    try:
        rconn.publish(redisserver.to_indi_channel, ebstring)
    except:
        ebstring = None
    return ebstring

        
    
def clearredis(rconn, redisserver):
    """Deletes the redis keys, (not logs) returns None.

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: The redis server parameters
    :type redisserver: namedtuple
    """
    rconn.delete( _key(redisserver, "getProperties") )
    device_list = devices(rconn, redisserver)
    rconn.delete( _key(redisserver, "devices") )
    #rconn.delete( _key(redisserver, "logdata", "devices") )    
    rconn.delete( _key(redisserver, "messages") )
    #rconn.delete( _key(redisserver, "logdata", "messages") )
    for device in device_list:
        rconn.delete( _key(redisserver, "getProperties", "device", device) )
        rconn.delete( _key(redisserver, "devicemessages", device) )
        #rconn.delete( _key(redisserver, "logdata", "devicemessages", device) )
        property_list = properties(rconn, redisserver, device)
        rconn.delete( _key(redisserver, "properties", device) )
        #rconn.delete( _key(redisserver, "logdata", "properties", device) )
        for name in property_list:
            rconn.delete( _key(redisserver, "getProperties", "property", name, device) )
            rconn.delete( _key(redisserver, "attributes", name, device) )
            #rconn.delete( _key(redisserver, "logdata", "attributes", name, device) )
            elements_list = elements(rconn, redisserver, name, device)
            rconn.delete( _key(redisserver, "elements", name, device) )
            #rconn.delete( _key(redisserver, "logdata", "elements", name, device) )
            for elementname in elements_list:
                rconn.delete( _key(redisserver, "elementattributes", elementname, name, device) )
                #rconn.delete( _key(redisserver, "logdata", "elementattributes", elementname, name, device) )


def number_to_float(value):
    """The INDI spec allows a number of different number formats, given any, this returns a float

    :param value: A number string of a float, integer or sexagesimal
    :type value: String
    :return:  The number as a float
    :rtype: Float
    """
    # negative is True, if the value is negative
    negative = value.startswith("-")
    if negative:
        value = value.lstrip("-")
    # Is the number provided in sexagesimal form?
    if value == "":
        parts = [0, 0, 0]
    elif " " in value:
        parts = value.split(" ")
    elif ":" in value:
        parts = value.split(":")
    elif ";" in value:
        parts = value.split(";")
    else:
        # not sexagesimal
        parts = [value, "0", "0"]
    # Any missing parts should have zero
    if len(parts) == 2:
        # assume seconds are missing, set to zero
        parts.append("0")
    assert len(parts) == 3
    number_strings = list(x if x else "0" for x in parts)
    # convert strings to integers or floats
    number_list = []
    for part in number_strings:
        try:
            num = int(part)
        except ValueError:
            num = float(part)
        number_list.append(num)
    floatvalue = number_list[0] + (number_list[1]/60) + (number_list[2]/360)
    if negative:
        floatvalue = -1 * floatvalue
    return floatvalue


def format_number(value, indi_format):
    """This takes a float, and returns a formatted string

    :param value: A float to be formatted
    :type value: Float
    :param indi_format: An INDI number format string
    :type indi_format: String
    :return:  The number formatted accordingly
    :rtype: String
    """
    if (not indi_format.startswith("%")) or (not indi_format.endswith("m")):
        return indi_format % value
    # sexagesimal format
    if value<0:
        negative = True
        value = abs(value)
    else:
        negative = False
    # number list will be degrees, minutes, seconds
    number_list = [0,0,0]
    if isinstance(value, int):
        number_list[0] = value
    else:
        # get integer part and fraction part
        fractdegrees, degrees = math.modf(value)
        number_list[0] = int(degrees)
        mins = 60*fractdegrees
        fractmins, mins = math.modf(mins)
        number_list[1] = int(mins)
        number_list[2] = 60*fractmins

    # so number list is a valid degrees, minutes, seconds
    # degrees
    if negative:
        number = f"-{number_list[0]}:"
    else:
        number = f"{number_list[0]}:"
    # format string is of the form  %<w>.<f>m
    w,f = indi_format.split(".")
    w = w.lstrip("%")
    f = f.rstrip("m")
    if (f == "3") or (f == "5"):
        # no seconds, so create minutes value
        minutes = float(number_list[1]) + number_list[2]/60.0
        if f == "5":
            number += f"{minutes:04.1f}"
        else:
            number += f"{minutes:02.0f}"
    else:
        number += f"{number_list[1]:02d}:"
        seconds = float(number_list[2])
        if f == "6":
            number += f"{seconds:02.0f}"
        elif f == "8":
            number += f"{seconds:04.1f}"
        else:
            number += f"{seconds:05.2f}"

    # w is the overall length of the string, prepend with spaces to make the length up to w
    w = int(w)
    l = len(number)
    if w>l:
        number = " "*(w-l) + number
    return number





