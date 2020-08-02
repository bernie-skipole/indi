

import xml.etree.ElementTree as ET

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


def device_list(rconn, redisserver):
    "Returns a list of devices, uses redis smembers on key devices"
    devicekey = _key(redisserver, "devices")
    devices = rconn.smembers(devicekey)
    if not devices:
        return []
    return list(d.decode("utf-8") for d in devices)


def property_list(rconn, redisserver, device):
    "Returns a list of properties, uses redis smembers on key properties:device"
    propertykey = _key(redisserver, "properties", device)
    properties = rconn.smembers(propertykey)
    if not properties:
        return []
    return list(p.decode("utf-8") for p in properties)


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


def attributes_dict(rconn, redisserver, device, name):
    "Returns a dictionary of attributes for the property"
    key = _key(redisserver, "attributes", name, device)
    attdict = rconn.hgetall(key)
    if not attdict:
        return {}
    return {k.decode("utf-8"):v.decode("utf-8") for k,v in attdict.items()}


def elements(rconn, redisserver, device, name):
    "Returns a list of elements for the property"
    key = _key(redisserver, "elements", name, device)
    els = rconn.smembers(key)
    if not els:
        return []
    return list(e.decode("utf-8") for e in els)


def elements_dict(rconn, redisserver, device, name, elementname):
    "Returns a dictionary of element attributes"
    key = _key(redisserver, "elementattributes", elementname, name, device)
    eldict = rconn.hgetall(key)
    if not eldict:
        return {}
    return {k.decode("utf-8"):v.decode("utf-8") for k,v in eldict.items()}
    





