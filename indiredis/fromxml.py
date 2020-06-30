

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
    # notification is published on redis using the from_indi_channel
    channel = get_from_indi_channel()


    for child in root:
        if child.tag == "defTextVector":
            text_vector = TextVector(child)         # store the received data in a TextVector object
            text_vector.write(rconn)                # call the write method to store data in redis
            rconn.publish(channel, f"defTextVector:{text_vector.name}:{text_vector.device}")   # publishes an alert that property:device has changed
        elif child.tag == "defNumberVector":
            number_vector = NumberVector(child)
            number_vector.write(rconn)
            rconn.publish(channel, f"defNumberVector:{number_vector.name}:{number_vector.device}")
        elif child.tag == "defSwitchVector":
            switch_vector = SwitchVector(child)
            switch_vector.write(rconn)
            rconn.publish(channel, f"defSwitchVector:{switch_vector.name}:{switch_vector.device}")
        elif child.tag == "defLightVector":
            light_vector = LightVector(child)
            light_vector.write(rconn)
            rconn.publish(channel, f"defLightVector:{light_vector.name}:{text_vector.device}")
        elif child.tag == "defBLOBVector":
            blob_vector = BLOBVector(child)
            blob_vector.write(rconn)
            rconn.publish(channel, f"defBLOBVector:{blob_vector.name}:{blob_vector.device}")
        elif child.tag == "message":
            message = Message(child)
            message.write(rconn)
            if message.device:
                rconn.publish(channel, f"message:{message.device}")
            else:
                rconn.publish(channel, "message")
        elif child.tag == "delProperty":
            delprop = delProperty(child)
            delprop.write(rconn)
            if delprop.name:
                rconn.publish(channel, f"delProperty:{delprop.name}:{delprop.device}")
            else:
                rconn.publish(channel, f"delDevice:{delprop.device}")
        elif child.tag == "setTextVector":
            result = setVector(rconn, child)
            if result is None:
                continue
            name,device = result
            rconn.publish(channel, f"setTextVector:{name}:{device}")
        elif child.tag == "setNumberVector":
            result = setVector(rconn, child)
            if result is None:
                continue
            name,device = result
            rconn.publish(channel, f"setNumberVector:{name}:{device}")
        elif child.tag == "setSwitchVector":
            result = setVector(rconn, child)
            if result is None:
                continue
            name,device = result
            rconn.publish(channel, f"setSwitchVector:{name}:{device}")
        elif child.tag == "setLightVector":
            result = setVector(rconn, child)
            if result is None:
                continue
            name,device = result
            rconn.publish(channel, f"setLightVector:{name}:{device}")
        elif child.tag == "setBLOBVector":
            result = setVector(rconn, child)
            if result is None:
                continue
            name,device = result
            rconn.publish(channel, f"setBLOBVector:{name}:{device}")

