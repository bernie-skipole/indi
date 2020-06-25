

###################
#
#  fromxml
#
###################


"""Reads indi xml strings, parses them and places values into redis,
ready for reading by the web server."""


# if receive <setXXX> from Device
#  change record of value and/or state for the specified Property
# if receive <defProperty> from Device
#  if first time to see this device=
#    create new Device record
#  if first time to see this device+name combination
#    create new Property record within given Device
# if receive <delProperty> from Device
#  if includes device= attribute
#    if includes name= attribute
#      delete record for just the given Device+name
#    else
#      delete all records the given Device
#  else
#    delete all records for all devices


import xml.etree.ElementTree as ET


from .parsetypes import *



def receive_from_indiserver(data, redisserver):
    "receives xml data from the indiserver"
    rconn = open_redis(redisserver)
    # if no redis connection is possible, return
    if rconn is None:
        return
    
    # data comes in block of xml elements, not inside a root, so create a root
    # element 'commsroot'
    xmlstring = b"".join((b"<commsroot>", data, b"</commsroot>"))
    root = ET.fromstring(xmlstring)

    for child in root:
        if child.tag == "defTextVector":
            text_vector = ParseTextVector(child)
            text_vector.save_attributes(rconn)
        if child.tag == "defNumberVector":
            number_vector = ParseNumberVector(child)
            number_vector.save_attributes(rconn)
        if child.tag == "defSwitchVector":
            switch_vector = ParseSwitchVector(child)
            switch_vector.save_attributes(rconn)
        if child.tag == "defLightVector":
            light_vector = ParseLightVector(child)
            light_vector.save_attributes(rconn)
        if child.tag == "defBLOBVector":
            blob_vector = ParseBLOBVector(child)
            blob_vector.save_attributes(rconn)
        if child.tag == "message":
            message = ParseMessage(child)
            print(message.device, str(message))
    # devices are those received in this exchange, list of binary names
    devices = rconn.smembers(key('devices'))
    if devices:
        device_names = list(dn.decode("utf-8") for dn in devices)
        device_names.sort()
        print(device_names)

        for name in device_names:
            properties = rconn.smembers(key('properties', name))
            property_names = list(pn.decode("utf-8") for pn in properties)
            property_names.sort()
            print(name, property_names)

        # print attributes dictionary for property ACTIVE_DEVICES
        # note the keys and values in this dictionary will be binary values.
        print(rconn.hgetall(key('attributes','ACTIVE_DEVICES',device_names[0])))


