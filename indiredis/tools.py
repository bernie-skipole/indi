

############################## tools.py ######################################################
#
# This is a set of Python functions which read, and publish to your redis server
# You may find them useful when creating a client gui, if your gui is Python based.
#
# These open a redis connection, and return lists of devices, properties, elements etc.,
#
# Typically your script would start with:
#
###############################################################################################
# from indiredis import redis_server, tools
#
# redisserver = redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_',
#                          to_indi_channel='to_indi', from_indi_channel='from_indi')
#
# rconn = tools.open_redis(redisserver)
###############################################################################################
#
# and then using rconn and redisserver you could call upon the functions provided here


import xml.etree.ElementTree as ET

from datetime import datetime

import re

import redis




def _key(redisserver, *keys):
    "Add the prefix to keys, delimit keys with :"
    # example - if keys are 'device', 'property' this will result in a key of
    # 'keyprefixdevice:property'
    return redisserver.keyprefix + ":".join(keys)


def open_redis(redisserver):
    "Opens a redis connection, return None on failure"
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


def getProperties(rconn, redisserver, device="", name=""):
    """Sends getProperties request, returns the xml bytes string sent

        device, if given, is the device name, set as the device attribute of the xml element
        name, if given, is the property name, set as the name attribute of the xml element"""
    gP = ET.Element('getProperties')
    gP.set("version", "1.7")
    if device:
        gP.set("device", device)
        if name:
            gP.set("name", name)
    etstring = ET.tostring(gP)
    rconn.publish(redisserver.to_indi_channel, etstring)
    return etstring


def devices(rconn, redisserver):
    "Returns a list of devices, uses redis smembers on key devices"
    devicekey = _key(redisserver, "devices")
    deviceset = rconn.smembers(devicekey)
    if not deviceset:
        return []
    devicelist = list(d.decode("utf-8") for d in deviceset)
    devicelist.sort()
    return devicelist


def properties(rconn, redisserver, device):
    "Returns a list of properties, uses redis smembers on key properties:device"
    propertykey = _key(redisserver, "properties", device)
    propertyset = rconn.smembers(propertykey)
    if not propertyset:
        return []
    propertylist = list(p.decode("utf-8") for p in propertyset)
    propertylist.sort()
    return propertylist


def elements(rconn, redisserver, device, name):
    "Returns a set of elements for the property"
    elementkey = _key(redisserver, "elements", name, device)
    elementset = rconn.smembers(elementkey)
    if not elementset:
        return []
    elementlist = list(e.decode("utf-8") for e in elementset)
    elementlist.sort()
    return elementlist


def attributes_dict(rconn, redisserver, device, name):
    "Returns a dictionary of attributes for the property"
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
    

def last_log(rconn, redisserver, device=""):
    """Return the last log as (timestamp,data) or None if not available
       If device given, the last log from this device is returned"""
    if device:
        logkey = _key(redisserver, "logdata", device)
    else:
        logkey = _key(redisserver, "logdata")
    logentry = rconn.lindex(logkey, 0)
    if logentry is None:
        return
    return logentry.decode("utf-8").split(" ", maxsplit=1)



def get_logs(rconn, redisserver, number):
    "Return the number of logs as [(timestamp,data),..] or None if not available"
    logkey = _key(redisserver, "logdata")
    loglist = rconn.lrange(logkey, 0, number)
    if not loglist:
        return
    return [logentry.decode("utf-8").split(" ", maxsplit=1) for logentry in loglist]



def getProperties(rconn, redisserver, device="", name=""):
    """Sends getProperties request, returns the xml string sent, or None on failure

        device, if given, is the device name, set as the device attribute of the xml element
        name, if given, is the property name, set as the name attribute of the xml element"""
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
    "Deletes the redis keys apart from logs"
    device_list = devices(rconn, redisserver)
    rconn.delete( _key(redisserver, "devices") )
    rconn.delete( _key(redisserver, "messages") )
    for device in device_list:
        rconn.delete( _key(redisserver, "devicemessages", device) )
        property_list = properties(rconn, redisserver, device)
        rconn.delete( _key(redisserver, "properties", device) )
        for name in property_list:
            rconn.delete( _key(redisserver, "attributes", name, device) )
            elements_list = elements(rconn, redisserver, device, name)
            rconn.delete( _key(redisserver, "elements", name, device) )
            for elementname in elements_list:
                rconn.delete( _key(redisserver, "elementattributes", elementname, name, device) )







