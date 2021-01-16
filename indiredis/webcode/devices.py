
import pathlib
from datetime import datetime, timedelta
from time import sleep
from base64 import urlsafe_b64encode, urlsafe_b64decode
from zlib import adler32

from skipole import FailPage

from indi_mr import tools

from .setvalues import set_state



def _safekey(key):
    """Provides a base64 encoded key from a given key"""
    b64binarydata = urlsafe_b64encode(key.encode('utf-8')).rstrip(b"=")  # removes final '=' padding
    return b64binarydata.decode('ascii')


def _fromsafekey(safekey):
    """Decodes a base64 encoded key"""
    b64binarydata = safekey.encode('utf-8') # get the received data and convert to binary
    # add padding
    b64binarydata = b64binarydata + b"=" * (4-len(b64binarydata)%4)
    return urlsafe_b64decode(b64binarydata).decode('utf-8') # b64 decode, and convert to string


def devicelist(skicall):
    "Gets a list of devices and fill index devices page"
    # remove any device, group etc from call_data, since this page does not refer to a single device
    skicall.call_data.clear()
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    checksum1 = ''
    # get last message
    message = tools.last_message(rconn, redisserver)
    if message:
        skicall.page_data['message', 'para_text'] = message
        checksum1 += message
    devices = tools.devices(rconn, redisserver)
    if not devices:
        skicall.page_data['device', 'hide'] = True
        if message:
            skicall.page_data['message', 'para_text'] = message + "\n\nAwaiting device information."
        else:
            skicall.page_data['message', 'para_text'] = "Awaiting device information."
        skicall.page_data['devicelist', 'para_text'] = "No devices have been found .. waiting for update."
        # publish getProperties
        getProperties(skicall)
        checksum1 += skicall.page_data['message', 'para_text']
        # encode checksum1 as binary, then create a checksum
        bindata = checksum1.encode('utf-8', errors='ignore')
        skicall.call_data["checksum1"] = adler32(bindata)
        return
    skicall.page_data['devicelist', 'para_text'] = "Follow the link to manage each instrument."
    # devices is a list of known devices
    skicall.page_data['device','multiplier'] = len(devices)
    for index,devicename in enumerate(devices):
        skicall.page_data['device_'+str(index),'devicename', 'button_text'] = devicename
        skicall.page_data['device_'+str(index),'devicename','get_field1'] = devicename
        checksum1 += devicename
        # set device messages here
        devicemessage = tools.last_message(rconn, redisserver, devicename)
        if devicemessage:
            skicall.page_data['device_'+str(index),'devicemessage','para_text'] = devicemessage
            checksum1 += devicemessage
    # encode checksum1 as binary, then create a checksum
    bindata = checksum1.encode('utf-8', errors='ignore')
    skicall.call_data["checksum1"] = adler32(bindata)


def check_for_update(skicall):
    """Called to update the devices page, which should occur every five seconds.
       If a change has occurred, requests the client re call the home page.
       If not, checks if getProperties has been sent in the last minute. If not,
       then send it."""

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    rxchecksum1 = skicall.call_data.get("checksum1", -1)
    devices = tools.devices(rconn, redisserver)
    if not devices:
        # no devices! Request browser to do a full page update
        skicall.page_data['JSONtoHTML'] = 'home'
        return
    checksum1 = ''
    # check if last message changed
    message = tools.last_message(rconn, redisserver)
    if message:
        checksum1 += message
    # devices is a list of known devices
    for index,devicename in enumerate(devices):
        checksum1 += devicename
        # set device messages here
        devicemessage = tools.last_message(rconn, redisserver, devicename)
        if devicemessage:
            checksum1 += devicemessage
    # encode checksum1 as binary, then create a checksum
    bindata = checksum1.encode('utf-8', errors='ignore')
    check = adler32(bindata)
    if check != rxchecksum1:
        # data read from redis is not the same as that currently shown
        # so request browser to do a full page update
        skicall.page_data['JSONtoHTML'] = 'home'


def propertylist(skicall):
    "Gets a list of properties for the given device"
    # Called from the links on the index list of devices page
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
    skicall.call_data["device"] = devicename
    refreshproperties(skicall)


def changegroup(skicall):
    "Called by group navigation, sets the group to be displayed"
    devicename = skicall.call_data.get("device","")
    if not devicename:
        raise FailPage("Device not recognised")
    if ('navlinks', 'get_field1') not in skicall.call_data:
        raise FailPage("Group not recognised")
    skicall.call_data['group'] = skicall.call_data['navlinks', 'get_field1']
    # and refresh the properties on the page
    refreshproperties(skicall)


def getProperties(skicall):
    "Sends getProperties request"
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    # publish getProperties
    textsent = tools.getProperties(rconn, redisserver)
    # print(textsent)


def getDeviceProperties(skicall):
    "Sends getProperties request for a given device, and refresh properties page"
    # gets device from page_data, which is set into skicall.call_data["device"] 
    devicename = skicall.call_data.get("device","")
    if not devicename:
        raise FailPage("Device not recognised")
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    # publish getProperties
    textsent = tools.getProperties(rconn, redisserver, device=devicename)
    # print(textsent)
    # wait two seconds for the data to hopefully refresh
    sleep(2)
    # and refresh the properties on the page
    refreshproperties(skicall)



def _read_redis(skicall):
    """Reads redis and returns a dictionary of device and its properties for the properties page
       and checksums for the displayed property page"""
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    # gets device from skicall.call_data["device"]
    devicename = skicall.call_data.get("device")
    if devicename is None:
        raise FailPage("No device has been specified")
    # check devicename is a valid device
    devices = tools.devices(rconn, redisserver)
    if not devices:
        # no devices!
        raise FailPage("No devices have been found")
    if devicename not in devices:
        # device has been deleted, go to home
        raise FailPage("The specified device has not been found")


    pdict = {"devicename":devicename}   # checks if any property has changed in the current displayed group
    hlist = []                          # checks if any property that requires a html refresh has changed

    # hlist will have all items added to it, that if changed, will require an html change
    # a string version of hlist will then be used to create a checksum

    properties = tools.properties(rconn, redisserver, devicename)
    # this is a list of property names, if any changes, then a full html refresh should happen
    if not properties:
        raise FailPage("No properties for the device have been found")
    pdict['properties'] = properties
    hlist.append(properties)

    # get last message and last device message, these can be updated by json, so do not require html
    # refresh, and so do not appear in hlist
    message = tools.last_message(rconn, redisserver)
    if message:
        pdict['message'] = message
    devicemessage = tools.last_message(rconn, redisserver, devicename)
    if devicemessage:
        pdict['devicemessage'] = devicemessage

    # create list of property attributes dictionaries
    att_list = []        # record property attributes - used to sort properties on the page
    for propertyname in properties:
        # get the property attributes
        att_dict = tools.attributes_dict(rconn, redisserver, propertyname, devicename)
        # Ensure the label is set
        label = att_dict.get('label')
        if label is None:
            att_dict['label'] = propertyname
        att_list.append(att_dict)


    # now sort att_list by group and then by label
    att_list.sort(key = lambda ad : (ad.get('group'), ad.get('label')))

    # get a list of groups for the group navigation bar
    # if the group_list has changed (perhaps new properties with a new group has arrived)
    # then this requires a html refresh
    group_set = set(ad['group'] for ad in att_list)
    group_list = sorted(group_set)
    pdict['group_list'] = group_list
    hlist.append(group_list)
    group = skicall.call_data.get('group')
    # could be None, if called from the home devices page, display the first group
    if group is None:
        group = group_list[0]
    if group not in group_list:
        raise FailPage("The group specified has not been recognised")
    pdict['group'] = group

    # record properties which are in the group being displayed
    # If new properties appear in this group, then a html refresh is needed
    propertygroup = []
    for ad in att_list:
        if att_dict['group'] == group:
            propertygroup.append(ad['name'])
    pdict['propertygroup'] = propertygroup
    hlist.append(propertygroup)

    # group_att_list is att_list limited to group members
    group_att_list = []
    for ad in att_list:
        # loops through each property, where ad is the attribute directory of the property
        # Only display the properties with the given group attribute
        if group == ad['group']:
            group_att_list.append(ad)

    # a html refresh is only needed for those properties in this group which are not number vectors
    numbervectors = []   # record properties which are numbervectors in this group
    not_numbers  = []
    for ad in group_att_list:
        # loops through each property in the group, where ad is the attribute directory of the property
        # for every property in the group_att_list, there is a list of element dictionaries which could change
        ad["elements"] = tools.property_elements(rconn, redisserver, ad['name'], ad['device'])
        if ad['vector'] == "NumberVector":
            numbervectors.append(ad['name'])
        else:
            not_numbers.append(ad)
    hlist.append(not_numbers)
    # so if any of these change, which includes property attributes and elements, a full refresh is needed

    pdict['numbervectors'] = numbervectors
    # However, a number vector could have more or fewer elements, or with different names.
    # in which case that also requires an html change
    element_names = []
    for ad in group_att_list:
        # get list of element names for the given property and device
        element_names.append( tools.elements(rconn, redisserver, ad['name'], ad['device']) )
    hlist.append(element_names)

    # temporarily set pdict['att_list'] to group_att_list so the checksum1 can be calculated
    pdict['att_list'] = group_att_list

    # create checksums from string values of pdict and hlist

    # work out checksum1
    # encode the string of pdict as binary, then create a checksum
    bindata1 = str(pdict).encode('utf-8', errors='ignore')
    checksum1 = adler32(bindata1)
    # replace pdict['att_list'] as att_list
    pdict['att_list'] = att_list
    # work out checksum2
    bindata2 = str(hlist).encode('utf-8', errors='ignore')
    checksum2 = adler32(bindata2)

    return pdict, checksum1, checksum2


def refreshproperties(skicall):
    "Reads redis and refreshes the properties page"
    # read properties from redis
    pdict, checksum1, checksum2 = _read_redis(skicall)
    # set checksum's into ident_data which is sent back and can be used to check if the page has changed
    skicall.call_data["checksum1"] = checksum1
    skicall.call_data["checksum2"] = checksum2
    skicall.page_data['devicename', 'large_text'] = pdict['devicename']
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    if 'message' in pdict:
        skicall.page_data['message', 'para_text'] = pdict['message']
    if 'devicemessage' in pdict:
        skicall.page_data['devicemessage','para_text'] = pdict['devicemessage']
    # properties is a list of properties for the given device
    # create a section for each property, and fill it in
    properties = pdict['properties']
    skicall.page_data['property','multiplier'] = len(properties)
    group = pdict['group']
    skicall.call_data["group"] = group
    link_classes = []
    link_buttons = []
    link_getfields = []
    for gp in pdict['group_list']:
        link_buttons.append(gp)
        link_getfields.append(gp)
        # highlight the bar item chosen
        if gp == group:
            link_classes.append("w3-bar-item w3-button w3-mobile w3-blue")
        else:
            link_classes.append("w3-bar-item w3-button w3-mobile")
    skicall.page_data['navlinks', 'button_classes'] = link_classes
    skicall.page_data['navlinks', 'button_text'] = link_buttons
    skicall.page_data['navlinks', 'get_field1'] = link_getfields
    att_list = pdict['att_list']
    for index, ad in enumerate(att_list):
        # loops through each property, where ad is the attribute directory of the property
        # and index is the section index on the web page
        # Only display the properties with the given group attribute
        if group == ad['group']:
            skicall.page_data['property_'+str(index),'show'] = True
        else:
            skicall.page_data['property_'+str(index),'show'] = False
            # This property is not being shown on the page, so continue
            continue
        # and display the property
        if ad['vector'] == "TextVector":
            _show_textvector(skicall, index, ad)
        elif ad['vector'] == "NumberVector":
            _show_numbervector(skicall, index, ad)
        elif ad['vector'] == "SwitchVector":
            _show_switchvector(skicall, index, ad)
        elif ad['vector'] == "LightVector":
            _show_lightvector(skicall, index, ad)
        elif ad['vector'] == "BLOBVector":
            _show_blobvector(skicall, index, ad)
        else:
            skicall.page_data['property_'+str(index),'propertyname', 'large_text'] = ad['label']
            skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']



def _show_textvector(skicall, index, ad):
    """ad is the attribute directory of the property
       index is the section index on the web page"""
    skicall.page_data['property_'+str(index),'propertyname', 'large_text'] = ad['label']
    skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']
    skicall.page_data['property_'+str(index),'textvector', 'show'] = True
    # list the attributes, group, state, perm, timeout, timestamp
    skicall.page_data['property_'+str(index),'tvtable', 'col1'] = [ "Perm:", "Timeout:", "Timestamp:"]
    skicall.page_data['property_'+str(index),'tvtable', 'col2'] = [ ad['perm'], ad['timeout'], ad['timestamp']]
    # set the state, one of Idle, OK, Busy and Alert
    set_state(skicall, index, ad)
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    element_list = ad["elements"]
    if not element_list:
        return
    # permission is one of ro, wo, rw
    if ad['perm'] == "wo":
        # permission is wo
        # display label : "" : text input field followed by a submit button
        skicall.page_data['property_'+str(index),'settext', 'show'] = True
        skicall.page_data['property_'+str(index),'tvtexttable', 'show'] = True
        col1 = []
        col2 = []
        inputdict = {}
        for eld in element_list:
            col1.append(eld['label'] + ":")
            inputdict[_safekey(eld['name'])] = ""  # all empty values, as write only
        skicall.page_data['property_'+str(index),'tvtexttable', 'col1'] = col1
        skicall.page_data['property_'+str(index),'tvtexttable', 'col2'] = col2   # all empty values
        skicall.page_data['property_'+str(index),'tvtexttable', 'inputdict'] = inputdict
        skicall.page_data['property_'+str(index),'tvtexttable', 'size'] = 30   # maxsize of input field
        # set hidden fields on the form
        skicall.page_data['property_'+str(index),'settext', 'propertyname'] = ad['name']
        skicall.page_data['property_'+str(index),'settext', 'sectionindex'] = index
    elif ad['perm'] == "rw":
        # permission is rw
        # display label : value : text input field followed by a submit button
        skicall.page_data['property_'+str(index),'settext', 'show'] = True
        skicall.page_data['property_'+str(index),'tvtexttable', 'show'] = True
        col1 = []
        col2 = []
        inputdict = {}
        maxsize = 0
        for eld in element_list:
            col1.append(eld['label'] + ":")
            col2.append(eld['value'])
            inputdict[_safekey(eld['name'])] = eld['value']
        if len(eld['value']) > maxsize:
            maxsize = len(eld['value'])
        skicall.page_data['property_'+str(index),'tvtexttable', 'col1'] = col1
        skicall.page_data['property_'+str(index),'tvtexttable', 'col2'] = col2
        skicall.page_data['property_'+str(index),'tvtexttable', 'inputdict'] = inputdict
        # make the size of the input field match the values set in it
        if maxsize > 30:
            maxsize = 30
        elif maxsize < 15:
            maxsize = 15
        else:
            maxsize += 1
        skicall.page_data['property_'+str(index),'tvtexttable', 'size'] = maxsize
        # set hidden fields on the form
        skicall.page_data['property_'+str(index),'settext', 'propertyname'] = ad['name']
        skicall.page_data['property_'+str(index),'settext', 'sectionindex'] = index
    else:
        # permission is ro
        # display label : value in a table
        skicall.page_data['property_'+str(index),'tvelements', 'show'] = True
        col1 = []
        col2 = []
        for eld in element_list:
            col1.append(eld['label'] + ":")
            col2.append(eld['value'])
        skicall.page_data['property_'+str(index),'tvelements', 'col1'] = col1
        skicall.page_data['property_'+str(index),'tvelements', 'col2'] = col2


def _show_numbervector(skicall, index, ad):
    """ad is the attribute directory of the property
       index is the section index on the web page"""
    skicall.page_data['property_'+str(index),'propertyname', 'large_text'] = ad['label']
    skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']
    skicall.page_data['property_'+str(index),'numbervector', 'show'] = True
    # list the attributes, group, state, perm, timeout, timestamp
    skicall.page_data['property_'+str(index),'nvtable', 'col1'] = [ "Perm:", "Timeout:", "Timestamp:"]
    skicall.page_data['property_'+str(index),'nvtable', 'col2'] = [ ad['perm'], ad['timeout'], ad['timestamp']]
    # set the state, one of Idle, OK, Busy and Alert
    set_state(skicall, index, ad)
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    element_list = ad["elements"]
    if not element_list:
        return
    # permission is one of ro, wo, rw
    if ad['perm'] == "wo":
        # permission is wo
        # display label : "" : numberinput field with minimum value, followed by a submit button
        skicall.page_data['property_'+str(index),'setnumber', 'show'] = True
        skicall.page_data['property_'+str(index),'nvinputtable', 'show'] = True
        col1 = []
        col2 = []
        # hide or not the up down arrow keys
        up_hide = []
        down_hide = []
        # up down keys need to identify the element
        up_getfield1 = []
        down_getfield1 = []
        inputdict = {}
        for elindex, eld in enumerate(element_list):
            # elindex will be used to get the number of the element as sorted on the table
            # and will be sent with the arrows get field
            col1.append(eld['label'] + ":")
            # set the input field to the minimum value
            inputdict[_safekey(eld['name'])] = tools.format_number(eld['float_min'], eld['format'])
            # make 1st getfield a combo of propertyname, element index, element name
            getfield1 = _safekey(ad['name'] + "\n" + str(elindex) + "\n" + eld['name'])
            up_getfield1.append(getfield1)
            down_getfield1.append(getfield1)
            if eld['step'] == '0':
                # no steps
                up_hide.append(True)
                down_hide.append(True)
            else:
                # set to the minimum, show up arrow, hide the down arrow
                up_hide.append(False)
                down_hide.append(True)
        skicall.page_data['property_'+str(index),'nvinputtable', 'col1'] = col1
        skicall.page_data['property_'+str(index),'nvinputtable', 'col2'] = col2
        skicall.page_data['property_'+str(index),'nvinputtable', 'inputdict'] = inputdict
        skicall.page_data['property_'+str(index),'nvinputtable', 'up_hide'] = up_hide
        skicall.page_data['property_'+str(index),'nvinputtable', 'up_getfield1'] = up_getfield1
        skicall.page_data['property_'+str(index),'nvinputtable', 'down_hide'] = down_hide
        skicall.page_data['property_'+str(index),'nvinputtable', 'down_getfield1'] = down_getfield1
        skicall.page_data['property_'+str(index),'nvinputtable', 'size'] = 30    # maxsize of input field
        # set hidden fields on the form
        skicall.page_data['property_'+str(index),'setnumber', 'propertyname'] = ad['name']
        skicall.page_data['property_'+str(index),'setnumber', 'sectionindex'] = index
    elif ad['perm'] == "rw":
        # permission is rw
        # display label : value : numberinput field followed by a submit button
        skicall.page_data['property_'+str(index),'setnumber', 'show'] = True
        skicall.page_data['property_'+str(index),'nvinputtable', 'show'] = True
        col1 = []
        col2 = []
        # hide or not the up down arrow keys
        up_hide = []
        down_hide = []
        # up down keys need to identify the element
        up_getfield1 = []
        down_getfield1 = []
        inputdict = {}
        maxsize = 0
        for elindex, eld in enumerate(element_list):
            # elindex will be used to get the number of the element as sorted on the table
            # and will be sent with the arrows get field
            col1.append(eld['label'] + ":")
            col2.append(eld['formatted_number'])
            inputdict[_safekey(eld['name'])] = eld['formatted_number']
            # make 1st getfield a combo of propertyname, element index, element name
            getfield1 = _safekey(ad['name'] + "\n" + str(elindex) + "\n" + eld['name'])
            up_getfield1.append(getfield1)
            down_getfield1.append(getfield1)
            if eld['step'] == '0':
                # no steps
                up_hide.append(True)
                down_hide.append(True)
            elif eld['float_number'] <= eld['float_min']:
                # at the minimum, hide the down arrow
                up_hide.append(False)
                down_hide.append(True)
            elif (eld['max'] != eld['min']) and (eld['float_number'] >= eld['float_max']):
                # at the maximum, hide the up arrow
                up_hide.append(True)
                down_hide.append(False)
            else:
                # steps are not zero and value is between min and max, so show arrows
                up_hide.append(False)
                down_hide.append(False)
        if len(eld['formatted_number']) > maxsize:
            maxsize = len(eld['formatted_number'])
        skicall.page_data['property_'+str(index),'nvinputtable', 'col1'] = col1
        skicall.page_data['property_'+str(index),'nvinputtable', 'col2'] = col2
        skicall.page_data['property_'+str(index),'nvinputtable', 'inputdict'] = inputdict
        skicall.page_data['property_'+str(index),'nvinputtable', 'up_hide'] = up_hide
        skicall.page_data['property_'+str(index),'nvinputtable', 'up_getfield1'] = up_getfield1
        skicall.page_data['property_'+str(index),'nvinputtable', 'down_hide'] = down_hide
        skicall.page_data['property_'+str(index),'nvinputtable', 'down_getfield1'] = down_getfield1
        # make the size of the input field match the values set in it
        if maxsize > 30:
            maxsize = 30
        elif maxsize < 15:
            maxsize = 15
        else:
            maxsize += 1
        skicall.page_data['property_'+str(index),'nvinputtable', 'size'] = maxsize
        # set hidden fields on the form
        skicall.page_data['property_'+str(index),'setnumber', 'propertyname'] = ad['name']
        skicall.page_data['property_'+str(index),'setnumber', 'sectionindex'] = index
    else:
        # permission is ro
        # display label : value in a table, no form as this table is not submitted
        skicall.page_data['property_'+str(index),'nvelements', 'show'] = True
        col1 = []
        col2 = []
        for eld in element_list:
            col1.append(eld['label'] + ":")
            col2.append(eld['formatted_number'])
        skicall.page_data['property_'+str(index),'nvelements', 'col1'] = col1
        skicall.page_data['property_'+str(index),'nvelements', 'col2'] = col2


def _show_switchvector(skicall, index, ad):
    """ad is the attribute directory of the property
       index is the section index on the web page"""
    skicall.page_data['property_'+str(index),'propertyname', 'large_text'] = ad['label']
    skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']
    skicall.page_data['property_'+str(index),'switchvector', 'show'] = True
    # list the attributes, group, rule, perm, timeout, timestamp
    skicall.page_data['property_'+str(index),'svtable', 'col1'] = [ "Rule", "Perm:", "Timeout:", "Timestamp:"]
    skicall.page_data['property_'+str(index),'svtable', 'col2'] = [ ad['rule'], ad['perm'], ad['timeout'], ad['timestamp']]

    # switchRule  is OneOfMany|AtMostOne|AnyOfMany

    # AtMostOne means zero or one  - so must add a 'none of the above button'
    # whereas OneOfMany means one must always be chosen

    # set the state, one of Idle, OK, Busy and Alert
    set_state(skicall, index, ad)

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    element_list = ad["elements"]
    if not element_list:
        return
    # permission is one of ro, wo, rw
    if ad['perm'] == "wo":
        # permission is wo
        if (ad['rule'] == "OneOfMany") and (len(element_list) == 1):
            # only one element, but rule is OneOfMany, so must give an off/on choice, with button names name_on and name_off
            skicall.page_data['property_'+str(index),'setswitch', 'show'] = True
            skicall.page_data['property_'+str(index),'svradio', 'show'] = True
            eld = element_list[0]
            skicall.page_data['property_'+str(index),'svradio', 'col1'] = [eld['label'] + ":"]
            skicall.page_data['property_'+str(index),'svradio', 'col2'] = ["On", "Off"]
            skicall.page_data['property_'+str(index),'svradio', 'radiocol'] = [eld['name'] + "_on", eld['name'] + "_off"]
            skicall.page_data['property_'+str(index),'svradio', 'row_classes'] = ['', '']
        elif ad['rule'] == "OneOfMany":
            # show radiobox, at least one should be pressed
            skicall.page_data['property_'+str(index),'setswitch', 'show'] = True
            skicall.page_data['property_'+str(index),'svradio', 'show'] = True
            col1 = []
            radiocol = []
            row_classes = []
            for eld in element_list:
                col1.append(eld['label'] + ":")
                radiocol.append(eld['name'])
                row_classes.append('')
            skicall.page_data['property_'+str(index),'svradio', 'col1'] = col1
            skicall.page_data['property_'+str(index),'svradio', 'radiocol'] = radiocol
            skicall.page_data['property_'+str(index),'svradio', 'row_classes'] = row_classes
        elif ad['rule'] == "AnyOfMany":
            skicall.page_data['property_'+str(index),'setswitch', 'show'] = True
            skicall.page_data['property_'+str(index),'svcheckbox', 'show'] = True
            col1 = []
            checkbox_dict = {}
            row_classes = []
            for eld in element_list:
                col1.append(eld['label'] + ":")
                checkbox_dict[eld['name']] = "On"
                row_classes.append('')
            skicall.page_data['property_'+str(index),'svcheckbox', 'col1'] = col1
            skicall.page_data['property_'+str(index),'svcheckbox', 'checkbox_dict'] = checkbox_dict
            skicall.page_data['property_'+str(index),'svcheckbox', 'row_classes'] = row_classes
        elif ad['rule'] == "AtMostOne":
            # show radiobox, can have none pressed
            skicall.page_data['property_'+str(index),'setswitch', 'show'] = True
            skicall.page_data['property_'+str(index),'svradio', 'show'] = True
            col1 = []
            radiocol = []
            row_classes = []
            for eld in element_list:
                col1.append(eld['label'] + ":")
                radiocol.append(eld['name'])
                row_classes.append('')
            # append a 'None of the above' button
            col1.append("None of the above:")
            radiocol.append("noneoftheabove")
            row_classes.append('')
            skicall.page_data['property_'+str(index),'svradio', 'col1'] = col1
            skicall.page_data['property_'+str(index),'svradio', 'radiocol'] = radiocol
            skicall.page_data['property_'+str(index),'svradio', 'row_classes'] = row_classes

        # set hidden fields on the form
        skicall.page_data['property_'+str(index),'setswitch', 'propertyname'] = ad['name']
        skicall.page_data['property_'+str(index),'setswitch', 'sectionindex'] = index

    elif ad['perm'] == "rw":
        if (ad['rule'] == "OneOfMany") and (len(element_list) == 1):
            # only one element, but rule is OneOfMany, so must give an off/on choice, with button names name_on and name_off
            skicall.page_data['property_'+str(index),'setswitch', 'show'] = True
            skicall.page_data['property_'+str(index),'svradio', 'show'] = True
            eld = element_list[0]
            skicall.page_data['property_'+str(index),'svradio', 'col1'] = [eld['label'] + ":"]
            skicall.page_data['property_'+str(index),'svradio', 'col2'] = ["On", "Off"]
            skicall.page_data['property_'+str(index),'svradio', 'radiocol'] = [eld['name'] + "_on", eld['name'] + "_off"]
            if eld['value'] == "On":
                skicall.page_data['property_'+str(index),'svradio', 'radio_checked'] = eld['name'] + "_on"
                skicall.page_data['property_'+str(index),'svradio', 'row_classes'] = ['w3-yellow', '']
            else:
                skicall.page_data['property_'+str(index),'svradio', 'radio_checked'] = eld['name'] + "_off"
                skicall.page_data['property_'+str(index),'svradio', 'row_classes'] = ['', 'w3-yellow']
        elif ad['rule'] == "OneOfMany":
            # show radiobox, at least one should be pressed
            skicall.page_data['property_'+str(index),'setswitch', 'show'] = True
            skicall.page_data['property_'+str(index),'svradio', 'show'] = True
            col1 = []
            col2 = []
            radiocol = []
            row_classes = []
            checked = None
            for eld in element_list:
                col1.append(eld['label'] + ":")
                col2.append(eld['value'])
                radiocol.append(eld['name'])
                if eld['value'] == "On":
                    checked = eld['name']
                    row_classes.append('w3-yellow')
                else:
                    row_classes.append('')
            skicall.page_data['property_'+str(index),'svradio', 'col1'] = col1
            #skicall.page_data['property_'+str(index),'svradio', 'col2'] = col2
            skicall.page_data['property_'+str(index),'svradio', 'radiocol'] = radiocol
            skicall.page_data['property_'+str(index),'svradio', 'row_classes'] = row_classes
            if checked:
                skicall.page_data['property_'+str(index),'svradio', 'radio_checked'] = checked
        elif ad['rule'] == "AnyOfMany":
            skicall.page_data['property_'+str(index),'setswitch', 'show'] = True
            skicall.page_data['property_'+str(index),'svcheckbox', 'show'] = True
            col1 = []
            col2 = []
            checkbox_dict = {}
            row_classes = []
            checked = []
            for eld in element_list:
                col1.append(eld['label'] + ":")
                col2.append(eld['value'])
                checkbox_dict[eld['name']] = "On"
                if eld['value'] == "On":
                    checked.append(eld['name'])
                    row_classes.append('w3-yellow')
                else:
                    row_classes.append('')
            skicall.page_data['property_'+str(index),'svcheckbox', 'col1'] = col1
            #skicall.page_data['property_'+str(index),'svcheckbox', 'col2'] = col2
            skicall.page_data['property_'+str(index),'svcheckbox', 'checkbox_dict'] = checkbox_dict
            skicall.page_data['property_'+str(index),'svcheckbox', 'row_classes'] = row_classes
            if checked:
                skicall.page_data['property_'+str(index),'svcheckbox', 'checked'] = checked
        elif ad['rule'] == "AtMostOne":
            # show radiobox, can have none pressed
            skicall.page_data['property_'+str(index),'setswitch', 'show'] = True
            skicall.page_data['property_'+str(index),'svradio', 'show'] = True
            col1 = []
            col2 = []
            radiocol = []
            row_classes = []
            checked = None
            for eld in element_list:
                col1.append(eld['label'] + ":")
                col2.append(eld['value'])
                radiocol.append(eld['name'])
                if eld['value'] == "On":
                    checked = eld['name']
                    row_classes.append('w3-yellow')
                else:
                    row_classes.append('')
            # append a 'None of the above' button
            col1.append("None of the above:")
            radiocol.append("noneoftheabove")
            if checked is None:
                col2.append("On")
                checked = "noneoftheabove"
                row_classes.append('w3-yellow')
            else:
                col2.append("Off")
                row_classes.append('')
            skicall.page_data['property_'+str(index),'svradio', 'col1'] = col1
            #skicall.page_data['property_'+str(index),'svradio', 'col2'] = col2
            skicall.page_data['property_'+str(index),'svradio', 'radiocol'] = radiocol
            skicall.page_data['property_'+str(index),'svradio', 'row_classes'] = row_classes
            skicall.page_data['property_'+str(index),'svradio', 'radio_checked'] = checked

        # set hidden fields on the form
        skicall.page_data['property_'+str(index),'setswitch', 'propertyname'] = ad['name']
        skicall.page_data['property_'+str(index),'setswitch', 'sectionindex'] = index

    else:
        # permission is ro
        # display label : value in a table
        skicall.page_data['property_'+str(index),'svelements', 'show'] = True
        col1 = []
        col2 = []
        for eld in element_list:
            col1.append(eld['label'] + ":")
            col2.append(eld['value'])
        skicall.page_data['property_'+str(index),'svelements', 'col1'] = col1
        skicall.page_data['property_'+str(index),'svelements', 'col2'] = col2


def _show_lightvector(skicall, index, ad):
    """ad is the attribute directory of the property
       index is the section index on the web page"""
    skicall.page_data['property_'+str(index),'propertyname', 'large_text'] = ad['label']
    skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']
    skicall.page_data['property_'+str(index),'lightvector', 'show'] = True
    # list the attributes, group, timestamp
    skicall.page_data['property_'+str(index),'lvproperties', 'contents'] = [ "Group: " + ad['group'],
                                                                             "Timestamp: " + ad['timestamp'] ]
    skicall.page_data['property_'+str(index),'lvtable', 'col1'] = [ "Group:", "Timestamp:"]
    skicall.page_data['property_'+str(index),'lvtable', 'col2'] = [ ad['group'], ad['timestamp']]

    # set the state, one of Idle, OK, Busy and Alert
    set_state(skicall, index, ad)

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    element_list = ad["elements"]
    if not element_list:
        return
    # No permission value for lightvectors
    # display label : value in a table
    col1 = []
    col2 = []
    for eld in element_list:
        col1.append(eld['label'] + ":")
        col2.append(eld['value'])
    skicall.page_data['property_'+str(index),'lvelements', 'col1'] = col1
    skicall.page_data['property_'+str(index),'lvelements', 'col2'] = col2



def _show_blobvector(skicall, index, ad):
    """ad is the attribute directory of the property
       index is the section index on the web page"""
    skicall.page_data['property_'+str(index),'propertyname', 'large_text'] = ad['label']
    skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']
    skicall.page_data['property_'+str(index),'blobvector', 'show'] = True


    # set the state, one of Idle, OK, Busy and Alert
    set_state(skicall, index, ad)

    # list the attributes, perm, timeout, timestamp and receive blobs status (if not write only)
    if ad['perm'] == "wo":
        skicall.page_data['property_'+str(index),'bvtable', 'col1'] = [ "Perm:", "Timeout:", "Timestamp:"]
        skicall.page_data['property_'+str(index),'bvtable', 'col2'] = [ ad['perm'], ad['timeout'], ad['timestamp']]
        skicall.page_data['property_'+str(index), 'enableblob', 'show'] = False   # do not show the enable blob button
        skicall.page_data['property_'+str(index), 'endescription', 'show'] = False   # do not show the enable description
    else:
        # if ro or rw then add the Receive Blobs status, enabled or disabled
        skicall.page_data['property_'+str(index),'bvtable', 'col1'] = [ "Perm:", "Timeout:", "Timestamp:", "Receive BLOB's:"]
        skicall.page_data['property_'+str(index),'bvtable', 'col2'] = [ ad['perm'], ad['timeout'], ad['timestamp'], ad['blobs']]
        # set the enableblob button
        if ad['blobs'] == "Enabled":
            # make get_field1 a combo of propertyname, Disable
            get_field1 = _safekey(ad['name'] + "\nDisable")
            skicall.page_data['property_'+str(index), 'enableblob', 'button_text'] = "Disable"
            skicall.page_data['property_'+str(index), 'enableblob', 'get_field1'] = get_field1
        else:
            # make get_field1 a combo of propertyname, Enable
            get_field1 = _safekey(ad['name'] + "\nEnable")
            skicall.page_data['property_'+str(index), 'enableblob', 'button_text'] = "Enable"
            skicall.page_data['property_'+str(index), 'enableblob', 'get_field1'] = get_field1

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    button_class = "w3-button w3-block w3-theme-d4"
    button_style = "width:15em;"
    element_list = ad["elements"]
    if not element_list:
        return
    # permission is one of ro, wo, rw
    if ad['perm'] == "wo":
        # permission is write only
        # set the modal upload box into the page, initially hidden
        skicall.page_data['modalupload', 'show'] = True
        skicall.page_data['modalupload', 'hide'] = True
        # display label : button to display upload
        skicall.page_data['property_'+str(index),'bvwelements', 'show'] = True
        col1 = []
        col2 = []
        col2_link_idents = []
        col2_json_idents = []
        col2_getfields = []
        link_classes = []
        link_styles = []
        for eld in element_list:
            col1.append(eld['label'] + ":")
            col2.append("Upload File")
            col2_link_idents = ["no_javascript"]
            col2_json_idents.append("show_modalupload")
            # make getfield a combo of propertyname, element name
            getfield = _safekey(ad['name'] + "\n" + eld['name'])
            col2_getfields.append(getfield)
            link_classes.append(button_class)
            link_styles.append(button_style)
        skicall.page_data['property_'+str(index),'bvwelements', 'col1'] = col1
        skicall.page_data['property_'+str(index),'bvwelements', 'col2'] = col2
        skicall.page_data['property_'+str(index),'bvwelements', 'col2_link_idents'] = col2_link_idents
        skicall.page_data['property_'+str(index),'bvwelements', 'col2_json_idents'] = col2_json_idents
        skicall.page_data['property_'+str(index),'bvwelements', 'col2_getfields'] = col2_getfields
        skicall.page_data['property_'+str(index),'bvwelements', 'link_classes'] = link_classes
        skicall.page_data['property_'+str(index),'bvwelements', 'link_styles'] = link_styles
    elif ad['perm'] == "rw":
        # set the modal upload box into the page, initially hidden
        # permission is read write
        skicall.page_data['modalupload', 'show'] = True
        skicall.page_data['modalupload', 'hide'] = True
        skicall.page_data['property_'+str(index),'bvwelements', 'show'] = True
        col1 = []
        col2 = []
        col2_link_idents = []
        col2_json_idents = []
        col2_getfields = []
        link_classes = []
        link_styles = []
        # note, there are two rows of the table for each element, one for received data, and one for the upload button
        for eld in element_list:
            # 1st row
            col1.append(eld['label'] + ":")
            if eld['filepath']:
                path = pathlib.Path(eld['filepath'])
                col2.append(path.name)
                col2_link_idents.append(f"/blobs/{path.name}")
            else:
                col2.append("")
                col2_link_idents.append("")
            # no json or get field in first row
            col2_json_idents.append("")
            col2_getfields.append("")
            link_classes.append('')
            link_styles.append('')
            # 2nd row
            col1.append("Send a file to the instrument:")
            col2.append("Upload File")
            col2_link_idents.append("no_javascript")
            col2_json_idents.append("show_modalupload")
            # make getfield a combo of propertyname, element name
            getfield = _safekey(ad['name'] + "\n" + eld['name'])
            col2_getfields.append(getfield)
            link_classes.append(button_class)
            link_styles.append(button_style)
        skicall.page_data['property_'+str(index),'bvwelements', 'col1'] = col1
        skicall.page_data['property_'+str(index),'bvwelements', 'col2'] = col2
        skicall.page_data['property_'+str(index),'bvwelements', 'col2_link_idents'] = col2_link_idents
        skicall.page_data['property_'+str(index),'bvwelements', 'col2_json_idents'] = col2_json_idents
        skicall.page_data['property_'+str(index),'bvwelements', 'col2_getfields'] = col2_getfields
        skicall.page_data['property_'+str(index),'bvwelements', 'link_classes'] = link_classes
        skicall.page_data['property_'+str(index),'bvwelements', 'link_styles'] = link_styles
        # take off the border at the bottem of every row
        skicall.page_data['property_'+str(index),'bvwelements', 'widget_class'] = "w3-table w3-centered"
        # and add it, just for even rows
        skicall.page_data['property_'+str(index),'bvwelements', 'even_class'] = "w3-border-bottom"
    else:
        # permission is read only
        # display label : filepath in a table
        skicall.page_data['property_'+str(index),'bvelements', 'show'] = True
        col1 = []
        col2 = []
        col2_links = []
        for eld in element_list:
            col1.append(eld['label'] + ":")
            if eld['filepath']:
                path = pathlib.Path(eld['filepath'])
                col2.append(path.name)
                col2_links.append(f"/blobs/{path.name}")
        skicall.page_data['property_'+str(index),'bvelements', 'col1'] = col1
        if col2:
            skicall.page_data['property_'+str(index),'bvelements', 'col2'] = col2
        if col2_links:
            skicall.page_data['property_'+str(index),'bvelements', 'col2_links'] = col2_links


def show_modalupload(skicall):
    "Display the modal upload box"
    skicall.page_data['modalupload', 'hide'] = False
    # device name should already be set in ident_data with skicall.call_data["device"]
    received_data = skicall.submit_dict['received_data']
    # example of  received_data
    #
    # {('property_0', 'bvwelements', 'col2_getfields'): 'aXJ0ZXN0Ml9ibG9iCmlydGVzdDJfYmxvYl9iMQ'}
    try:
        keys = list(received_data.keys())
        propertyindex = keys[0][0]
        p,sectionindex = propertyindex.split("_")
    except:
        raise FailPage("Invalid data")
    if p != "property":
        raise FailPage("Invalid data")
    if (propertyindex, 'bvwelements', 'col2_getfields') not in received_data:
        raise FailPage("Invalid data")
    try:
        rxdata = received_data[propertyindex, 'bvwelements', 'col2_getfields']
        data = _fromsafekey(rxdata)
        propertyname, elementname = data.split("\n")
    except:
        raise FailPage("Invalid data")
    # set upload widget hidden field with this data, so it is submitted with the file to upload
    skicall.page_data['upblob', 'hidden_field1'] = _safekey(propertyname + "\n" + sectionindex + "\n" + elementname)





def check_for_device_change(skicall):
    """Called to update the properties page, which should occur every ten seconds"""
    # The page which has called for this update shows all the properties in
    # a particular group, and the device, group and checksums should all be present
    # in call_data
    if (('device' not in skicall.call_data) or 
        ('group' not in skicall.call_data) or 
        ('checksum1' not in skicall.call_data) or
        ('checksum2' not in skicall.call_data)):
        # something wrong, divert to the home page
        skicall.page_data['JSONtoHTML'] = 'home'
        return
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    pdict, checksum1, checksum2 = _read_redis(skicall)
    devicename = pdict["devicename"]
    if (checksum1 == skicall.call_data['checksum1']) and (checksum2 == skicall.call_data['checksum2']):
        # generated checksums are equal to the received checksums so
        # no update required
        return

    # so an update is needed, it could be a whole page html, or just those items which can be changed by json
    # if checksum2 is unchanged, this means those items requiring a whole page refresh (groups, propertynames)
    # are unchanged, and therefore only a json refresh is needed

    if checksum2 != skicall.call_data['checksum2']:
        # the whole page needs refreshing, request the browser to make an html call
        skicall.page_data['JSONtoHTML'] = 'refreshproperties'
        return
        
    #############################################################################################################
    # To reach this point, only those items which can be updated by json have changed, therefore do a json update

    if 'message' in pdict:
        skicall.page_data['message', 'para_text'] = pdict['message']
    if 'devicemessage' in pdict:
        skicall.page_data['devicemessage','para_text'] = pdict['devicemessage']

    numbervectors = pdict['numbervectors']   # properties which are numbervectors
    att_list = pdict['att_list']             # property attributes - used to sort properties on the page

    # numbervectors are treated different to other vectors - they will have a json page update
    # whereas all other property changes will cause a full page refresh

    # refresh numbervectors in this group only

    for index, ad in enumerate(att_list):
        # loops through each property, where ad is the attribute directory of the property
        # and index is the section index on the web page
        propertyname = ad['name']
        if propertyname not in numbervectors:
            continue 
        
        # set the change into page data
        # items which may have changed:
        #            state
        #            timeout
        #            timestamp
        #            message
        #            elements:{name:number,...}

        # set the state, one of Idle, OK, Busy and Alert
        set_state(skicall, index, ad)
        skicall.page_data['property_'+str(index),'nvtable', 'col2'] = [ ad['perm'], ad['timeout'], ad['timestamp']]
        skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']

        element_list = ad["elements"]
        if not element_list:
            continue
        # permission is one of ro, wo, rw
        if ad['perm'] == "wo":
            continue             # if write only, should be no change from indiserver to display
        elif ad['perm'] == "rw":
            # permission is rw
            col2 = []
            inputdict = {}
            for eld in element_list:
                col2.append(eld['formatted_number'])
                inputdict[_safekey(eld['name'])] = eld['formatted_number']
            skicall.page_data['property_'+str(index),'nvinputtable', 'col2'] = col2
            skicall.page_data['property_'+str(index),'nvinputtable', 'inputdict'] = inputdict
        else:
            # permission is ro
            col2 = []
            for eld in element_list:
                col2.append(eld['formatted_number'])
            skicall.page_data['property_'+str(index),'nvelements', 'col2'] = col2

    # as this new data is inserted into the page, the page data should now have the same
    # checksums as the generated checksums

    skicall.call_data['checksum1'] = checksum1


