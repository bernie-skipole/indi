

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
        elif child.tag == "defNumberVector":
            number_vector = NumberVector(child)
            number_vector.write(rconn)
        elif child.tag == "defSwitchVector":
            switch_vector = SwitchVector(child)
            switch_vector.write(rconn)
        elif child.tag == "defLightVector":
            light_vector = LightVector(child)
            light_vector.write(rconn)
        elif child.tag == "defBLOBVector":
            blob_vector = BLOBVector(child)
            blob_vector.write(rconn)
        elif child.tag == "message":
            message = Message(child)
            message.write(rconn)
        elif child.tag == "delProperty":
            delprop = delProperty(child)
            delprop.write(rconn)
        elif child.tag == "setTextVector":
            setVector(rconn, child)
        elif child.tag == "setNumberVector":
            setVector(rconn, child)
        elif child.tag == "setSwitchVector":
            setVector(rconn, child)
        elif child.tag == "setLightVector":
            setVector(rconn, child)

    # tests

    x = readvector(rconn, 'Telescope Simulator', 'ACTIVE_DEVICES')
    print(f"{x.label}\n{x}")
        

### 'Telescope Simulator'


###'ACTIVE_DEVICES', 'CONFIG_PROCESS', 'CONNECTION', 'CONNECTION_MODE', 'DEBUG', 'DEVICE_AUTO_SEARCH', 'DEVICE_BAUD_RATE', 'DEVICE_PORT', 'DEVICE_PORT_SCAN'
### 'DOME_POLICY', 'DRIVER_INFO', 'POLLING_PERIOD', 'SCOPE_CONFIG_NAME', 'TELESCOPE_INFO'
