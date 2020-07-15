

import xml.etree.ElementTree as ET

import redis


def _key(redisserver, *keys):
    "Add the prefix to keys, delimit keys with :"
    # example - if keys are 'device', 'property' this will result in a key of
    # 'keyprefixdevice:property'
    return redisserver.keyprefix + ":".join(keys)


def open_redis(redisserver):
    "Opens a redis connection"
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
    "Returns a list of devices, uses smembers on key devices"
    devicekey = _key(redisserver, "devices")
    devices = rconn.smembers(devicekey)
    if not devices:
        return []
    return list(d.decode("utf-8") for d in devices)


def getProperties(rconn, redisserver, device="", name=""):
    "Sends getProperties request, if given device is the device name, if given name is the property name"
    gP = ET.Element('getProperties')
    gP.set("version", "1.7")
    if device:
        gP.set("device", device)
        if name:
            gP.set("name", name)
    rconn.publish(redisserver.to_indi_channel, ET.tostring(gP))

