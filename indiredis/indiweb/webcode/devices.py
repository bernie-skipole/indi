

from datetime import datetime
from time import sleep

from skipole import FailPage

from ... import tools

from .setvalues import set_state


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
        print(textsent)
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
    # gets device from page_data, which is set into skicall.call_data["device"] 
    devicename = skicall.call_data.get("device","")
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


def refreshproperties(skicall):
    "Reads redis and refreshes the properties page"
    # gets device from page_data, which is set into skicall.call_data["device"] 
    devicename = skicall.call_data.get("device","")
    if not devicename:
        raise FailPage("Device not recognised")
    # and refresh the properties on the page
    _findproperties(skicall, devicename)


def _findproperties(skicall, devicename):
    "Gets the properties for the device"
    skicall.page_data['devicename', 'large_text'] = devicename
    # set device and timestamp into ident_data so it will be available
    skicall.call_data["device"] = devicename
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
        att_dict = tools.attributes_dict(rconn, redisserver, devicename, propertyname)
        # Ensure the label is set
        label = att_dict.get('label')
        if label is None:
            att_dict['label'] = propertyname
        att_list.append(att_dict)
    # now sort it by group and then by label
    att_list.sort(key = lambda ad : (ad.get('group'), ad.get('label')))
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


def _show_textvector(skicall, index, ad):
    """ad is the attribute directory of the property
       index is the section index on the web page"""
    skicall.page_data['property_'+str(index),'propertyname', 'large_text'] = ad['label']
    skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']
    skicall.page_data['property_'+str(index),'textvector', 'show'] = True
    # list the attributes, group, state, perm, timeout, timestamp
    skicall.page_data['property_'+str(index),'tvtable', 'col1'] = [ "Group:", "Perm:", "Timeout:", "Timestamp:"]
    skicall.page_data['property_'+str(index),'tvtable', 'col2'] = [ ad['group'], ad['perm'], ad['timeout'], ad['timestamp']]

    # set the state, one of Idle, OK, Busy and Alert
    set_state(skicall, index, ad)

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    element_list = tools.property_elements(rconn, redisserver, ad['device'], ad['name'])
    if not element_list:
        return
    # permission is one of ro, wo, rw
    if ad['perm'] == "xx":   # wo
        pass                               ########## still to do
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
            inputdict[eld['name']] = eld['value']
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
    skicall.page_data['property_'+str(index),'nvtable', 'col1'] = [ "Group:", "Perm:", "Timeout:", "Timestamp:"]
    skicall.page_data['property_'+str(index),'nvtable', 'col2'] = [ ad['group'], ad['perm'], ad['timeout'], ad['timestamp']]


    # set the state, one of Idle, OK, Busy and Alert
    set_state(skicall, index, ad)

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    element_list = tools.property_elements(rconn, redisserver, ad['device'], ad['name'])
    if not element_list:
        return
    # permission is one of ro, wo, rw
    if ad['perm'] == "xx":   #wo
        pass                               ########## still to do
    elif ad['perm'] == "rw":
        # permission is rw
        # display label : value : numberinput field followed by a submit button
        skicall.page_data['property_'+str(index),'setnumber', 'show'] = True
        skicall.page_data['property_'+str(index),'nvinputtable', 'show'] = True
        col1 = []
        col2 = []
        inputdict = {}
        maxsize = 0
        for eld in element_list:
            col1.append(eld['label'] + ":")
            col2.append(eld['formatted_number'])
            inputdict[eld['name']] = eld['formatted_number']
        if len(eld['formatted_number']) > maxsize:
            maxsize = len(eld['formatted_number'])
        skicall.page_data['property_'+str(index),'nvinputtable', 'col1'] = col1
        skicall.page_data['property_'+str(index),'nvinputtable', 'col2'] = col2
        skicall.page_data['property_'+str(index),'nvinputtable', 'inputdict'] = inputdict
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
        # display label : value in a table
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
    skicall.page_data['property_'+str(index),'svtable', 'col1'] = [ "Group:", "Rule", "Perm:", "Timeout:", "Timestamp:"]
    skicall.page_data['property_'+str(index),'svtable', 'col2'] = [ ad['group'], ad['rule'], ad['perm'], ad['timeout'], ad['timestamp']]

    # switchRule  is OneOfMany|AtMostOne|AnyOfMany

    # AtMostOne means zero or one  - so must add a 'none of the above button'
    # whereas OneOfMany means one must always be chosen

    # set the state, one of Idle, OK, Busy and Alert
    set_state(skicall, index, ad)

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    element_list = tools.property_elements(rconn, redisserver, ad['device'], ad['name'])
    if not element_list:
        return
    # permission is one of ro, wo, rw
    if ad['perm'] == "xx":   #wo
        pass                               ########## still to do
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
    element_list = tools.property_elements(rconn, redisserver, ad['device'], ad['name'])
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
    skicall.page_data['property_'+str(index),'bvproperties', 'contents'] = [ "Group: " + ad['group'],
                                                                             "Perm: " + ad['perm'],
                                                                             "Timeout: " + ad['timeout'],
                                                                             "Timestamp: " + ad['timestamp'] ]
    # set the state, one of Idle, OK, Busy and Alert
    set_state(skicall, index, ad)

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    element_list = tools.property_elements(rconn, redisserver, ad['device'], ad['name'])
    if not element_list:
        return
    # list the elements
    contents = []
    for eld in element_list:
        contents.append(eld['label'] + " : " + eld['value'])
    skicall.page_data['property_'+str(index),'bvelements', 'contents'] = contents



def check_for_update(skicall):
    "When updating the devices page by json, update entire page if any change has occurred"
    if 'timestamp' in skicall.call_data:
        timestamp = skicall.call_data['timestamp']
    else:
        # device / timestamp not available, better refresh anyway
        skicall.page_data['JSONtoHTML'] = 'home'
        return
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    # check if last log has an older timestamp than this page
    logentry = tools.last_log(rconn, redisserver)
    if logentry is None:
        skicall.page_data['JSONtoHTML'] = 'home'
        return
    logtime, logdata = logentry
    if timestamp < logtime:
        # page timestamp is earlier than last log entry, so update the page
        skicall.page_data['JSONtoHTML'] = 'home'


def check_for_device_change(skicall):
    """Checks to see if a device has changed, in which case the properties page should have a html refresh
       If however only numbers have changed, then update just the numbers by JSON, without html refresh
       This is done since number change may be a common occurence as a measurement is tracked"""
    if ('device' in skicall.call_data) and ('timestamp' in skicall.call_data):
        devicename = skicall.call_data['device']
        timestamp = skicall.call_data['timestamp']
    else:
        # device / timestamp not available, better refresh anyway
        skicall.page_data['JSONtoHTML'] = 'refreshproperties'
        return
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    # check if last log for this device has an older timestamp than this page
    logentry = tools.last_log(rconn, redisserver, devicename)
    if logentry is None:
        skicall.page_data['JSONtoHTML'] = 'refreshproperties'
        return
    logtime, logdata = logentry
    if timestamp < logtime:
        # page timestamp is earlier than last log entry, so update the page
        skicall.page_data['JSONtoHTML'] = 'refreshproperties'
        return
    # check if any setnumber vectors have been updated after the page timestamp
    # if they have, return the change in a json call
    properties = tools.properties(rconn, redisserver, devicename)
    if not properties:
        raise FailPage("No properties for the device have been found")
    # for each property, check timestamp of last update
    att_list = []  # attributes needed to find index of property
    for propertyname in properties:
        # get the property attributes
        att_dict = tools.attributes_dict(rconn, redisserver, devicename, propertyname)
        # Ensure the label is set
        label = att_dict.get('label')
        if label is None:
            att_dict['label'] = propertyname
        att_list.append(att_dict)
    # now sort properties by group and then by label
    att_list.sort(key = lambda ad : (ad.get('group'), ad.get('label')))
    for index, ad in enumerate(att_list):
        # loops through each property, where ad is the attribute dictionary of the property
        # and index is the section index on the web page
        if ad['vector'] != "NumberVector":
            continue
        propertyname = ad['name']
        vector = tools.last_numbervector(rconn, redisserver, devicename, propertyname)
        if not vector:
            continue
        loggedtime, logdata = vector
        if timestamp > loggedtime:
            # page has been updated since this logged time, no need to update this vector
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
        skicall.page_data['property_'+str(index),'nvtable', 'col2'] = [ ad['group'], ad['perm'], ad['timeout'], ad['timestamp']]
        skicall.page_data['property_'+str(index),'propertyname', 'small_text'] = ad['message']

        element_list = tools.property_elements(rconn, redisserver, devicename, propertyname)
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
                inputdict[eld['name']] = eld['formatted_number']
            skicall.page_data['property_'+str(index),'nvinputtable', 'col2'] = col2
            skicall.page_data['property_'+str(index),'nvinputtable', 'inputdict'] = inputdict
        else:
            # permission is ro
            col2 = []
            for eld in element_list:
                col2.append(eld['formatted_number'])
            skicall.page_data['property_'+str(index),'nvelements', 'col2'] = col2






