

import xml.etree.ElementTree as ET

from time import sleep

from indiredis import tools

from skipole import FailPage


def devicelist(skicall):
    "Gets a list of devices"
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    devices = tools.devices(rconn, redisserver)
    # devices is a list of known devices
    skicall.page_data['device','multiplier'] = len(devices)
    for index,devicename in enumerate(devices):
        skicall.page_data['device_'+str(index),'devicename', 'button_text'] = devicename
        skicall.page_data['device_'+str(index),'devicename','get_field1'] = devicename


def propertylist(skicall):
    "Gets a list of properties for the given device"
    # Find the given device, given by responder
    # get data in skicall.submit_dict under key 'received'
    # with value being a dictionary with keys being the widgfield tuples of the submitting widgets
    # in this case, only one key should be given
    datadict = skicall.submit_dict['received']
    if len(datadict) != 1:
       raise FailPage("Invalid device")
    for dn in datadict.values():
        devicename = dn
    # redis key 'devices' - set of device names
    if not devicename:
        raise FailPage("Device not recognised")
    _findproperties(skicall, devicename)


def getProperties(skicall):
    "Sends getProperties request"
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    # publish getProperties
    textsent = tools.getProperties(rconn, redisserver)
    print(textsent)


def getDeviceProperties(skicall):
    "Sends getProperties request for a given device"
    devicename = skicall.call_data.get("devicename","")
    if not devicename:
        raise FailPage("Device not recognised")
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    # publish getProperties
    textsent = tools.getProperties(rconn, redisserver, device=devicename)
    print(textsent)
    # wait two seconds for the data to hopefully refresh
    sleep(2)
    # and refresh the properties on the page
    _findproperties(skicall, devicename)


def _findproperties(skicall, devicename):
    "Gets the properties for the device"
    skicall.page_data['devicename', 'large_text'] = devicename
    skicall.page_data['getprops','get_field1'] = devicename
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    properties = tools.properties(rconn, redisserver, devicename)
    if not properties:
        raise FailPage("No properties for the device have been found")
    # properties is a list of properties for the given device
    # create a section for each property, and fill it in
    skicall.page_data['property','multiplier'] = len(properties)
    # create list of property attributes dictionaries
    att_list = [] 
    for propertyname in properties:
        # get the property attributes
        att_dict = tools.attributes_dict(rconn, redisserver, devicename, propertyname)
        # Ensure the label is set
        label = att_dict.get('label')
        if label is None:
            att_dict['label'] = propertyname
        att_list.append(att_dict)
    # now sort it by group
    att_list.sort(key = lambda ad : ad.get('group'))
    for index, ad in enumerate(att_list):
        # loops through each property, where ad is the attribute directory of the property
        # and index is the section index on the web page
        if ad['vector'] == "TextVector":
            _show_textvector(skicall, index, ad)
        elif ad['vector'] == "NumberVector":
            _show_numbervector(skicall, index, ad)
        elif ad['vector'] == "SwitchVector":
            _show_switchvector(skicall, index, ad)
        elif ad['vector'] == "LightVector":
            _show_lightvector(skicall, index, ad)
        elif ad['vector'] == "BlobVector":
            _show_blobvector(skicall, index, ad)
        else:
            skicall.page_data['property_'+str(index),'propertyname', 'large_text'] = ad['label']
            skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']



def _set_state(skicall, index, ad):
    "Set the state, one of Idle, OK, Busy and Alert, with colours gray, green, yellow and red"
    state = ad['state']
    if state == "Idle":
        skicall.page_data['property_'+str(index),'state', 'widget_class'] = "w3-right w3-grey"
    elif state == "Ok":
        skicall.page_data['property_'+str(index),'state', 'widget_class'] = "w3-right w3-green"
    elif state == "Busy":
        skicall.page_data['property_'+str(index),'state', 'widget_class'] = "w3-right w3-yellow"
    else:
        # as default, state is Alert
        state = "Alert"
        skicall.page_data['property_'+str(index),'state', 'widget_class'] = "w3-right w3-red"
    skicall.page_data['property_'+str(index),'state', 'para_text'] = state



def _show_textvector(skicall, index, ad):
    """ad is the attribute directory of the property
       index is the section index on the web page"""
    skicall.page_data['property_'+str(index),'propertyname', 'large_text'] = ad['label']
    skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']
    skicall.page_data['property_'+str(index),'textvector', 'show'] = True
    # list the attributes, group, state, perm, timeout, timestamp
    skicall.page_data['property_'+str(index),'tvproperties', 'contents'] = [ "Group: " + ad['group'],
                                                                             "Perm: " + ad['perm'],
                                                                             "Timeout: " + ad['timeout'],
                                                                             "Timestamp: " + ad['timestamp'] ]
    # set the state, one of Idle, OK, Busy and Alert
    _set_state(skicall, index, ad)

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    element_list = tools.elements(rconn, redisserver, ad['device'], ad['name'])
    if not element_list:
        return
    # list the elements
    contents = []
    for element in element_list:
        eld = tools.elements_dict(rconn, redisserver, ad['device'], ad['name'], element)
        contents.append(eld['label'] + " : " + eld['value'])
    skicall.page_data['property_'+str(index),'tvelements', 'contents'] = contents



def _show_numbervector(skicall, index, ad):
    """ad is the attribute directory of the property
       index is the section index on the web page"""
    skicall.page_data['property_'+str(index),'propertyname', 'large_text'] = ad['label']
    skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']
    skicall.page_data['property_'+str(index),'numbervector', 'show'] = True
    # list the attributes, group, state, perm, timeout, timestamp
    skicall.page_data['property_'+str(index),'nvproperties', 'contents'] = [ "Group: " + ad['group'],
                                                                             "Perm: " + ad['perm'],
                                                                             "Timeout: " + ad['timeout'],
                                                                             "Timestamp: " + ad['timestamp'] ]
    # set the state, one of Idle, OK, Busy and Alert
    _set_state(skicall, index, ad)

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    element_list = tools.elements(rconn, redisserver, ad['device'], ad['name'])
    if not element_list:
        return
    # list the elements
    contents = []
    for element in element_list:
        eld = tools.elements_dict(rconn, redisserver, ad['device'], ad['name'], element)
        contents.append(eld['label'] + " : " + eld['formatted_number'])
    skicall.page_data['property_'+str(index),'nvelements', 'contents'] = contents



def _show_switchvector(skicall, index, ad):
    """ad is the attribute directory of the property
       index is the section index on the web page"""
    skicall.page_data['property_'+str(index),'propertyname', 'large_text'] = ad['label']
    skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']
    skicall.page_data['property_'+str(index),'switchvector', 'show'] = True
    # list the attributes, group, state, perm, timeout, timestamp
    skicall.page_data['property_'+str(index),'svproperties', 'contents'] = [ "Group: " + ad['group'],
                                                                             "Perm: " + ad['perm'],
                                                                             "Timeout: " + ad['timeout'],
                                                                             "Timestamp: " + ad['timestamp'] ]
    # set the state, one of Idle, OK, Busy and Alert
    _set_state(skicall, index, ad)

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    element_list = tools.elements(rconn, redisserver, ad['device'], ad['name'])
    if not element_list:
        return
    # list the elements
    contents = []
    for element in element_list:
        eld = tools.elements_dict(rconn, redisserver, ad['device'], ad['name'], element)
        contents.append(eld['label'] + " : " + eld['value'])
    skicall.page_data['property_'+str(index),'svelements', 'contents'] = contents



def _show_lightvector(skicall, index, ad):
    """ad is the attribute directory of the property
       index is the section index on the web page"""
    skicall.page_data['property_'+str(index),'propertyname', 'large_text'] = ad['label']
    skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']
    skicall.page_data['property_'+str(index),'lightvector', 'show'] = True
    # list the attributes, group, state, perm, timeout, timestamp
    skicall.page_data['property_'+str(index),'lvproperties', 'contents'] = [ "Group: " + ad['group'],
                                                                             "Timestamp: " + ad['timestamp'] ]
    # set the state, one of Idle, OK, Busy and Alert
    _set_state(skicall, index, ad)

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    element_list = tools.elements(rconn, redisserver, ad['device'], ad['name'])
    if not element_list:
        return
    # list the elements
    contents = []
    for element in element_list:
        eld = tools.elements_dict(rconn, redisserver, ad['device'], ad['name'], element)
        contents.append(eld['label'] + " : " + eld['value'])
    skicall.page_data['property_'+str(index),'lvelements', 'contents'] = contents


def _show_blobvector(skicall, index, ad):
    """ad is the attribute directory of the property
       index is the section index on the web page"""
    skicall.page_data['property_'+str(index),'propertyname', 'large_text'] = ad['label']
    skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']
    skicall.page_data['property_'+str(index),'blobvector', 'show'] = True
    # list the attributes, group, state, perm, timeout, timestamp
    skicall.page_data['property_'+str(index),'bvproperties', 'contents'] = [ "Group: " + ad['group'],
                                                                             "Perm: " + ad['perm'],
                                                                             "Timeout: " + ad['timeout'],
                                                                             "Timestamp: " + ad['timestamp'] ]
    # set the state, one of Idle, OK, Busy and Alert
    _set_state(skicall, index, ad)

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    element_list = tools.elements(rconn, redisserver, ad['device'], ad['name'])
    if not element_list:
        return
    # list the elements
    contents = []
    for element in element_list:
        eld = tools.elements_dict(rconn, redisserver, ad['device'], ad['name'], element)
        contents.append(eld['label'] + " : " + eld['value'])
    skicall.page_data['property_'+str(index),'bvelements', 'contents'] = contents


