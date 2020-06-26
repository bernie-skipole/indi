

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



def receive_from_indiserver(data, rconn):
    "receives xml data from the indiserver"

    if rconn is None:
        return
    
    # data comes in block of xml elements, not inside a root, so create a root
    # element 'commsroot'
    xmlstring = b"".join((b"<commsroot>", data, b"</commsroot>"))
    root = ET.fromstring(xmlstring)

    for child in root:
        if child.tag == "defTextVector":
            text_vector = TextVector(child)
            text_vector.write(rconn)
        if child.tag == "defNumberVector":
            number_vector = NumberVector(child)
            number_vector.write(rconn)
        if child.tag == "defSwitchVector":
            switch_vector = SwitchVector(child)
            switch_vector.write(rconn)
        if child.tag == "defLightVector":
            light_vector = LightVector(child)
            light_vector.write(rconn)
        if child.tag == "defBLOBVector":
            blob_vector = BLOBVector(child)
            blob_vector.write(rconn)
        if child.tag == "message":
            message = Message(child)
            message.write(rconn)
        if child.tag == "delProperty":
            delprop = delProperty(child)
            delprop.write(rconn)
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
            # any messages
            devicemessagelist = rconn.lrange(key('messages', name), 0, -1)
            if devicemessagelist:
                print(name, devicemessagelist)

        # print attributes dictionary for property ACTIVE_DEVICES
        # note the keys and values in this dictionary will be binary values.
        print(rconn.hgetall(key('attributes','ACTIVE_DEVICES',device_names[0])))

    # system message list
    system_messages = rconn.lrange(key('messages'), 0, -1)
    if system_messages:
        print(system_messages)

        


