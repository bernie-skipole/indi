

"""This is a set of Python functions which read, and publish to your redis server.
You may find them useful when creating a client gui, if your gui is Python based.

Functions are provided which open a redis connection, and return lists of devices, properties, elements etc.,

Your script could start with::

    from indiredis import redis_server, tools

    redisserver = redis_server(host='localhost', port=6379)
    rconn = tools.open_redis(redisserver)

and then using rconn and redisserver you could call upon the functions provided here.

Where a timestamp is specified, it will be a string according to the INDI v1.7 white paper which describes it as::

    A timeValue shall be specified in UTC in the form YYYY-MM-DDTHH:MM:SS.S. The final decimal and subsequent
    fractional seconds are optional and may be specified to whatever precision is deemed necessary by the transmitting entity.
    This format is in general accord with ISO 86015 and the Complete forms defined in W3C Note "Date and Time Formats"

"""


import xml.etree.ElementTree as ET

from datetime import datetime

import re, json

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

    :param redisserver: Named Tuple providing the redis server parameters
    :type redisserver: collections.namedtuple
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


def last_message(rconn, redisserver, device=""):
    """Return the last message or None if not available.
    If device given, the last message from this device is returned
    message is a string of timestamp space message text

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: Named Tuple providing the redis server parameters
    :type redisserver: collections.namedtuple
    :param device: If not given the message returned is the last message received without
                   a device specified. If given the message returned is the last which specified that device name.
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


def getProperties(rconn, redisserver, device="", name=""):
    """Publishes a getProperties request on the to_indi_channel. If device and name
    are not specified this is a general request for all devices and properties.

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: Named Tuple providing the redis server parameters
    :type redisserver: collections.namedtuple
    :param device: If given, should be the device name, and will be set as the device
                   attribute of the xml element sent
    :type device: String
    :param name: If given, should be the property name of the given device and will
                 be set as the name attribute of the xml element sent. If name is given
                 device must be given as well.
    :type name: String
    :return: A bytes string of the xml published, or None on failure
    :rtype: Bytes
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


def devices(rconn, redisserver):
    """Returns a list of devices, uses redis smembers on key devices
    applies the key prefix as defined in redisserver.

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: Named Tuple providing the redis server parameters
    :type redisserver: collections.namedtuple
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
    """Returns a list of property names for the given device, uses redis smembers
    on key properties:device, applies the key prefix as defined in redisserver.

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: Named Tuple providing the redis server parameters
    :type redisserver: collections.namedtuple
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

    :param rconn: A redis connection
    :type rconn: redis.client.Redis
    :param redisserver: Named Tuple providing the redis server parameters
    :type redisserver: collections.namedtuple
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
    :param redisserver: Named Tuple providing the redis server parameters
    :type redisserver: collections.namedtuple
    :param name: The property name
    :type name: String
    :param device: The device name
    :type device: String
    :return: A dictionary of attributes
    :rtype: Dict
    """
    attkey = _key(redisserver, "attributes", name, device)
    attdict = rconn.hgetall(attkey)
    if not attdict:
        return {}
    return {k.decode("utf-8"):v.decode("utf-8") for k,v in attdict.items()}


def elements_dict(rconn, redisserver, device, name, elementname):
    "Returns a dictionary of element attributes"
    elkey = _key(redisserver, "elementattributes", elementname, name, device)
    eldict = rconn.hgetall(elkey)
    if not eldict:
        return {}
    return {k.decode("utf-8"):v.decode("utf-8") for k,v in eldict.items()}


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


def property_elements(rconn, redisserver, device, name):
    """Returns a list of dictionaries of element attributes
       for the given device and property name
       each dictionary will be set in the list in order of label"""
    element_name_list = elements(rconn, redisserver, device, name)
    if not element_name_list:
        return []
    element_dictionary_list = list( elements_dict(rconn, redisserver, device, name, elementname) for elementname in element_name_list )
    # sort element_dictionary_list by label
    element_dictionary_list.sort(key=_split_element_labels)
    return element_dictionary_list


def logs(rconn, redisserver, number, *keys):
    """If number is 1, return the latest log as [timestamp,data],
       If number > 1 return the number of logs as [[timestamp,data], ...] or empty list if none available"""
    if number < 1:
        return []
    logkey = _key(redisserver, "logdata", *keys)
    if number == 1:
        logentry = rconn.lindex(logkey, 0)
        if logentry is None:
            return []
        logtime, logdata = logentry.decode("utf-8").split(" ", maxsplit=1)
        logdata = json.loads(logdata)
        return [logtime,logdata]
    logs = rconn.lrange(logkey, 0, number-1)
    if logs is None:
        return []
    nlogs = []
    for logentry in logs:
        logtime, logdata = logentry.decode("utf-8").split(" ", maxsplit=1)
        logdata = json.loads(logdata)
        nlogs.append([logtime,logdata])
    return nlogs






def newswitchvector(rconn, redisserver, device, name, values, timestamp=None):
    """Sends a newSwichVector request, returns the xml string sent, or None on failure
       values is a dictionary of name:state where name is the switch element name, state is On or Off
       timestamp is a datetime object, if None the current utc datetime will be used"""
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



def newtextvector(rconn, redisserver, device, name, values, timestamp=None):
    """Sends a newTextVector request, returns the xml string sent, or None on failure
       values is a dictionary of text names : values
       timestamp is a datetime object, if None the current utc datetime will be used"""
    ntv = ET.Element('newTextVector')
    ntv.set("device", device)
    ntv.set("name", name)
    if timestamp is None:
        ntv.set("timestamp", datetime.utcnow().isoformat(sep='T'))
    else:
        ntv.set("timestamp", timestamp.isoformat(sep='T'))
    # set the text elements 
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


def newnumbervector(rconn, redisserver, device, name, values, timestamp=None):
    """Sends a newNumberVector request, returns the xml string sent, or None on failure
       values is a dictionary of names : values
       timestamp is a datetime object, if None the current utc datetime will be used"""
    nnv = ET.Element('newNumberVector')
    nnv.set("device", device)
    nnv.set("name", name)
    if timestamp is None:
        nnv.set("timestamp", datetime.utcnow().isoformat(sep='T'))
    else:
        nnv.set("timestamp", timestamp.isoformat(sep='T'))
    # set the number elements 
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
        
    
def clearredis(rconn, redisserver):
    "Deletes the redis keys"
    device_list = devices(rconn, redisserver)
    rconn.delete( _key(redisserver, "devices") )
    rconn.delete( _key(redisserver, "logdata", "devices") )    
    rconn.delete( _key(redisserver, "messages") )
    rconn.delete( _key(redisserver, "logdata", "messages") )
    for device in device_list:
        rconn.delete( _key(redisserver, "devicemessages", device) )
        rconn.delete( _key(redisserver, "logdata", "devicemessages", device) )
        property_list = properties(rconn, redisserver, device)
        rconn.delete( _key(redisserver, "properties", device) )
        for name in property_list:
            rconn.delete( _key(redisserver, "attributes", name, device) )
            elements_list = elements(rconn, redisserver, device, name)
            rconn.delete( _key(redisserver, "elements", name, device) )
            for elementname in elements_list:
                rconn.delete( _key(redisserver, "elementattributes", elementname, name, device) )







