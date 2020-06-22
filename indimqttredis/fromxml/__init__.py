

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


from . import parsetypes



def receive_from_indiserver(data, redisserver):
    "receives xml data from the indiserver"
    rconn = parsetypes.open_redis(redisserver)
    # if no redis connection is possible, return
    if rconn is None:
        return
    
    # data comes in block of xml elements, not inside a root, so create a root
    # element 'commsroot'
    xmlstring = b"".join((b"<commsroot>", data, b"</commsroot>"))
    root = ET.fromstring(xmlstring)

    parsetypes.receive_tree(root)


               
    

