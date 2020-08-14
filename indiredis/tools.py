

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
    devicelist = rconn.smembers(devicekey)
    if not devicelist:
        return []
    return list(d.decode("utf-8") for d in devicelist)


def properties(rconn, redisserver, device):
    "Returns a list of properties, uses redis smembers on key properties:device"
    propertykey = _key(redisserver, "properties", device)
    propertylist = rconn.smembers(propertykey)
    if not propertylist:
        return []
    return list(p.decode("utf-8") for p in propertylist)


def elements(rconn, redisserver, device, name):
    "Returns a list of elements for the property"
    elementkey = _key(redisserver, "elements", name, device)
    elementlist = rconn.smembers(elementkey)
    if not elementlist:
        return []
    return list(e.decode("utf-8") for e in elementlist)


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
    





