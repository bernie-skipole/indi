
import pathlib
from datetime import datetime
from time import sleep
from base64 import urlsafe_b64encode

from skipole import FailPage

from ... import tools

from .setvalues import set_state


def _safekey(key):
    """Provides a base64 encoded key from a given key"""
    b64binarydata = urlsafe_b64encode(key.encode('utf-8')).rstrip(b"=")  # removes final '=' padding
    return b64binarydata.decode('ascii')

def devicelist(skicall):
    "Gets a list of devices and fill index devices page"
    # remove any device from call_data, since this page does not refer to a single device
    if "device" in skicall.call_data:
        del skicall.call_data["device"]
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    devices = tools.devices(rconn, redisserver)
    if not devices:
        skicall.page_data['device', 'hide'] = True
        skicall.page_data['message', 'para_text'] = "Awaiting device information."
        # publish getProperties
        textsent = tools.getProperties(rconn, redisserver)
        # print(textsent)
        return
    # get last message
    message = tools.last_message(rconn, redisserver)
    if message:
        skicall.page_data['message', 'para_text'] = message
    # devices is a list of known devices
    skicall.page_data['device','multiplier'] = len(devices)
    for index,devicename in enumerate(devices):
        skicall.page_data['device_'+str(index),'devicename', 'button_text'] = devicename
        skicall.page_data['device_'+str(index),'devicename','get_field1'] = devicename
        # to add device messages here
        devicemessage = tools.last_message(rconn, redisserver, devicename)
        if devicemessage:
            skicall.page_data['device_'+str(index),'devicemessage','para_text'] = devicemessage
    # set timestamp into call_data so the end_call function can insert it into ident_data
    skicall.call_data["timestamp"] = datetime.utcnow().isoformat(sep='T') 


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
    "Sends getProperties request for a given device"
    # gets device from page_data, which is set into skicall.call_data["device"] 
    devicename = skicall.call_data.get("device","")
    if not devicename:
        raise FailPage("Device not recognised")
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    # publish getProperties
    textsent = tools.getProperties(rconn, redisserver, device=devicename)
    # wait two seconds for the data to hopefully refresh
    sleep(2)
    # and refresh the properties on the page
    refreshproperties(skicall)


def refreshproperties(skicall):
    "Reads redis and refreshes the properties page"
    # gets device from skicall.call_data["device"] 
    devicename = skicall.call_data.get("device","")
    if not devicename:
        raise FailPage("Device not recognised")
    # and refresh the properties on the page
    skicall.page_data['devicename', 'large_text'] = devicename
    # set timestamp into call_data so the end_call function can insert it into ident_data
    skicall.call_data["timestamp"] = datetime.utcnow().isoformat(sep='T')
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    properties = tools.properties(rconn, redisserver, devicename)
    if not properties:
        raise FailPage("No properties for the device have been found")
    # get last message and last device message
    message = tools.last_message(rconn, redisserver)
    if message:
        skicall.page_data['message', 'para_text'] = message
    devicemessage = tools.last_message(rconn, redisserver, devicename)
    if devicemessage:
        skicall.page_data['devicemessage','para_text'] = devicemessage
    # properties is a list of properties for the given device
    # create a section for each property, and fill it in
    skicall.page_data['property','multiplier'] = len(properties)
    # create list of property attributes dictionaries
    att_list = []
    for propertyname in properties:
        # get the property attributes
        att_dict = tools.attributes_dict(rconn, redisserver, propertyname, devicename)
        # Ensure the label is set
        label = att_dict.get('label')
        if label is None:
            att_dict['label'] = propertyname
        att_list.append(att_dict)
    # get a set of groups for the group navigation bar
    group_set = set(ad.get('group', "No group") for ad in att_list)
    group_list = sorted(group_set)
    group = skicall.call_data.get('group')
    if (group is None) or (group not in group_list):
        group = group_list[0]
        skicall.call_data['group'] = group
    link_classes = []
    link_buttons = []
    link_getfields = []
    for gp in group_list:
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
    # now sort att_list by group and then by label
    att_list.sort(key = lambda ad : (ad.get('group'), ad.get('label')))
    for index, ad in enumerate(att_list):
        # loops through each property, where ad is the attribute directory of the property
        # and index is the section index on the web page

        # Only display the properties with the given group attribute
        if group == ad.get('group'):
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
    element_list = tools.property_elements(rconn, redisserver, ad['name'], ad['device'])
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
    element_list = tools.property_elements(rconn, redisserver, ad['name'], ad['device'])
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
    element_list = tools.property_elements(rconn, redisserver, ad['name'], ad['device'])
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
    element_list = tools.property_elements(rconn, redisserver, ad['name'], ad['device'])
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

    # list the attributes, group, state, perm, timeout, timestamp
    skicall.page_data['property_'+str(index),'bvtable', 'col1'] = [ "Perm:", "Timeout:", "Timestamp:", "Receive BLOB's:"]
    skicall.page_data['property_'+str(index),'bvtable', 'col2'] = [ ad['perm'], ad['timeout'], ad['timestamp'], ad['blobs']]

    # set the state, one of Idle, OK, Busy and Alert
    set_state(skicall, index, ad)

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
    element_list = tools.property_elements(rconn, redisserver, ad['name'], ad['device'])
    if not element_list:
        return
    # permission is one of ro, wo, rw
    if ad['perm'] == "xx":   # wo
        pass                               ########## still to do
    elif ad['perm'] == "yy": #rw
        pass                               ########## still to do
    else:
        # permission is ro
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


def _check_logs(skicall, *args):
    """Checks logs defined by *args, and if changed after the timestamp
       given in skicall returns True"""
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    timestamp = skicall.call_data['timestamp']
    logentry = tools.logs(rconn, redisserver, 1, *args)
    if logentry:
        logtime, logdata = logentry[0]
        if timestamp < logtime:
            # page timestamp is earlier than last log entry
            return True
    return False



def check_for_update(skicall):
    """When updating the devices page by json, update entire page if any change has occurred
       This means check the devices log, the messages log, and for every device, the devicemessages log"""
    if 'timestamp' not in skicall.call_data:
        skicall.page_data['JSONtoHTML'] = 'home'
        return
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    devices = tools.devices(rconn, redisserver)
    if not devices:
        # no devices! Keep updating
        skicall.page_data['JSONtoHTML'] = 'home'
        return
    # check if devices has a later timestamp than this page
    if _check_logs(skicall, 'devices'):
        skicall.page_data['JSONtoHTML'] = 'home'
        return
    # check if messages has a later timestamp than this page
    if _check_logs(skicall, 'messages'):
        skicall.page_data['JSONtoHTML'] = 'home'
        return
    # For every device, check if devicemessages has a later timestamp than this page
    for device in devices:
        if _check_logs(skicall, 'devicemessages', device):
            skicall.page_data['JSONtoHTML'] = 'home'
            return
    # No update has been made, so do not refresh the page

 

def check_for_device_change(skicall):
    """Checks to see if a device has changed, in which case the properties page should have a html refresh
       If however only numbers have changed, then update just the numbers by JSON, without html refresh
       This is done since number change may be a common occurence as a measurement is tracked"""
    # The device page which has called for this update should list all the properties in
    # a particular group, and the device, timestamp and group should all be present
    if ('device' not in skicall.call_data) or ('timestamp' not in skicall.call_data):
        skicall.page_data['JSONtoHTML'] = 'home'
        return
    devicename = skicall.call_data['device']
    timestamp = skicall.call_data['timestamp']
    group = skicall.call_data.get('group')
    if group is None:
        # something is wrong
        raise FailPage("Invalid data, no group has been specified in the request")
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    # check devicename is a valid device
    devices = tools.devices(rconn, redisserver)
    if not devices:
        # no devices! go to home
        skicall.page_data['JSONtoHTML'] = 'home'
        return
    if devicename not in devices:
        # device has been deleted, go to home
        skicall.page_data['JSONtoHTML'] = 'home'
        return
    # are properties present for this device
    properties = tools.properties(rconn, redisserver, devicename)
    if not properties:
        raise FailPage("No properties for the device have been found")
    # now check logs

    # if a devicemessage has updated, refresh the page
    if _check_logs(skicall, 'devicemessages', devicename):
        skicall.page_data['JSONtoHTML'] = 'refreshproperties'
        return

    # check if property names found for this device has a later timestamp than this page
    if _check_logs(skicall, 'properties', devicename):
        skicall.page_data['JSONtoHTML'] = 'refreshproperties'
        return

    # numbervectors are treated different to other vectors - they will have a json page update
    # whereas all other property changes will cause a full page refresh
    # check if attributes of a property have changed, and also list numbervectors
    numbervectors = []   # record properties which are numbervectors
    propertygroup = []   # record properties which are in the group being displayed
    att_list = []        # record property attributes - used to sort properties on the page
    for propertyname in properties:
        # get the property attributes
        att_dict = tools.attributes_dict(rconn, redisserver, propertyname, devicename)
        # Ensure the label is set
        label = att_dict.get('label')
        if label is None:
            att_dict['label'] = propertyname
        att_list.append(att_dict)
        if att_dict['group'] == group:
            propertygroup.append(propertyname)
        if att_dict['vector'] == "NumberVector":
            numbervectors.append(propertyname)
        else:
            # if any property other than a number vector has changed attributes, refresh the page
            if _check_logs(skicall, 'attributes', propertyname, devicename):
                skicall.page_data['JSONtoHTML'] = 'refreshproperties'
                return

    # for every property in the displayed group, other than numbervectors, check elements have not changed
    for propertyname in propertygroup:
        if propertyname in numbervectors:
            continue
        elements = tools.property_elements(rconn, redisserver, propertyname, devicename)
        # elements is a list of dictionaries of element attributes
        if not elements:
            continue
        # check if element names for this property has changed
        if _check_logs(skicall, 'elements', propertyname, devicename):
            skicall.page_data['JSONtoHTML'] = 'refreshproperties'
            return
        # check for updated element attributes
        for elementdict in elements:
            # check if attribute has changed
            if _check_logs(skicall, 'elementattributes', elementdict['name'], propertyname, devicename):
                skicall.page_data['JSONtoHTML'] = 'refreshproperties'
                return

    # for numbervectors in this group only, if there has been a change
    # set property name :elements list into updatedict
    updatedict = {}
    for propertyname in numbervectors:
        if propertyname not in propertygroup:
            continue
        elements = tools.property_elements(rconn, redisserver, propertyname, devicename)
        # elements is a list of dictionaries of element attributes
        if not elements:
            continue
        # check if element names for this property has changed
        if _check_logs(skicall, 'elements', propertyname, devicename):
            skicall.page_data['JSONtoHTML'] = 'refreshproperties'
            return
        # check for updated property attributes
        logentry = tools.logs(rconn, redisserver, 1, 'attributes', propertyname, devicename)
        if logentry:
            logtime, logdata = logentry[0]
            if timestamp < logtime:
                updatedict[propertyname] = elements
                # property needs to be updated
                continue
        # check for updated element attributes
        for elementdict in elements:
            logentry = tools.logs(rconn, redisserver, 1, 'elementattributes', elementdict['name'], propertyname, devicename)
            if logentry:
                logtime, logdata = logentry[0]
                if timestamp < logtime:
                    updatedict[propertyname] = elements
                    # property needs to be updated, do not bother checking further elements in the property
                    break

    # updatedict keys are the property names needing updating,
    # values are the list of element attribute dictionaries within that property
    if updatedict:
        # this property has to be updated
        # sort att_list by group and then by label
        att_list.sort(key = lambda ad : (ad.get('group'), ad.get('label')))
        for index, ad in enumerate(att_list):
            # loops through each property, where ad is the attribute directory of the property
            # and index is the section index on the web page
            propertyname = ad['name']
            if propertyname not in updatedict:
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

            element_list = updatedict[propertyname]
            if not element_list:
                continue
            # permission is one of ro, wo, rw
            if ad['perm'] == "xx":   #wo
                continue                              ########## still to do
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
        # and since the page has been updated, update the timestamp
        # in call_data so the end_call function can insert it into ident_data
        skicall.call_data["timestamp"] = datetime.utcnow().isoformat(sep='T')




