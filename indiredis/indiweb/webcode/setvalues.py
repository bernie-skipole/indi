
from skipole import FailPage

from ... import tools

## hiddenfields are
#
# propertyname
# sectionindex


def set_state(skicall, index, state):
    """Set the state, which is either a string or a dictionary, if it is a dictionary
       the actual state should be set under key 'state'
       The state set is one of Idle, OK, Busy and Alert, with colours gray, green, yellow and red"""
    if isinstance(state, dict):
        setstate = state['state']
    else:
        setstate = state
    if setstate == "Idle":
        skicall.page_data['property_'+str(index),'state', 'widget_class'] = "w3-right w3-grey"
    elif setstate == "Ok":
        skicall.page_data['property_'+str(index),'state', 'widget_class'] = "w3-right w3-green"
    elif setstate == "Busy":
        skicall.page_data['property_'+str(index),'state', 'widget_class'] = "w3-right w3-yellow"
    else:
        # as default, state is Alert
        setstate = "Alert"
        skicall.page_data['property_'+str(index),'state', 'widget_class'] = "w3-right w3-red"
    skicall.page_data['property_'+str(index),'state', 'para_text'] = setstate


def _check_received_data(skicall, setstring):
    """setstring should be one of 'settext', 'setswitch', 'setnumber'
       Returns devicename, propertyindex, sectionindex, propertyname
       where devicename is the device
             propertyindex is, for example, 'property_4'
             sectionindex is, for example, '4'
             propertyname is the property"""

    if skicall.ident_data:
        devicename = skicall.call_data["device"]
    else:
        raise FailPage("Unknown device")

    received_data = skicall.submit_dict['received_data']

    # example of  received_data
    #
    # {
    # ('property_4', 'settext', 'sectionindex'): '4',
    # ('property_4', 'settext', 'propertyname'): 'DEVICE_PORT',
    # ('property_4', 'tvtexttable', 'inputdict'): {'PORT': '/dev/ttyUSB0'}
    # }

    try:
        keys = list(received_data.keys())
        propertyindex = keys[0][0]
        p,sectionindex = propertyindex.split("_")
    except:
        raise FailPage("Invalid data")

    if p != "property":
        raise FailPage("Invalid data")

    if (propertyindex, setstring, 'sectionindex') not in received_data:
        raise FailPage("Invalid data")
    
    # sectionindex should be equal to the provided sectionindex
    if received_data[(propertyindex, setstring, 'sectionindex')] != sectionindex:
        raise FailPage("Invalid data")

    propertyname = received_data[propertyindex, setstring, 'propertyname']

    return devicename, propertyindex, sectionindex, propertyname



def set_switch(skicall):
    "Responds to a submission to set a switch vector"
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    devicename, propertyindex, sectionindex, propertyname = _check_received_data(skicall, 'setswitch')
    # get list of element names for this property
    names = tools.elements(rconn, redisserver, devicename, propertyname)
    if not names:
        raise FailPage("Error parsing data")
    # initially set all element switch values to be Off
    valuedict = {nm:'Off' for nm in names}
    received_data = skicall.submit_dict['received_data']
    if (propertyindex, 'svradio', 'radio_checked') in received_data:
        # a value has been received from a radio control
        value = received_data[propertyindex, 'svradio', 'radio_checked']
        if len(names) == 1:
            # only one element, can be either on or off
            # this value is a string of the format name or name_on or name_off
            if value.endswith("_on"):
                ename = value[0:-3]
                if ename in names:
                    valuedict = {ename : "On"}
                else:
                    raise FailPage("Error parsing data")
            elif value.endswith("_off"):
                ename = value[0:-4]
                if ename in names:
                    valuedict = {ename : "Off"}
                else:
                    raise FailPage("Error parsing data")
            else:
                # only one value, but does not end in _on or _off
                raise FailPage("Error parsing data")
        else:
            # multiple names, but only one received, and to be set to On
            # however if value is noneoftheabove, then all should be Off
            if value != "noneoftheabove":
                if value in names:
                    valuedict[value] = "On"
                else:
                    raise FailPage("Error parsing data")
        data_sent = tools.newswitchvector(rconn, redisserver, devicename, propertyname, valuedict)
        print(data_sent)
        if not data_sent:
            raise FailPage("Error sending data")
    elif (propertyindex, 'svcheckbox', 'checked') in received_data:
        # a dictionary of keys values has been received from a checkbox control
        value = received_data[propertyindex, 'svcheckbox', 'checked']
        # Only need keys, as all values of checked items are 'On'
        for ename in value.keys():
            if ename in names:
                valuedict[ename] = "On"
            else:
                raise FailPage("Error sending data")
        data_sent = tools.newswitchvector(rconn, redisserver, devicename, propertyname, valuedict)
        print(data_sent)
        if not data_sent:
            raise FailPage("Error sending data")
    else:
        skicall.call_data["status"] = "Unable to parse received data"
        return
    set_state(skicall, sectionindex, "Busy")
    skicall.call_data["status"] = f"Change to property {propertyname} has been submitted" 


def set_text(skicall):
    "Responds to a submission to set a text vector"
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    devicename, propertyindex, sectionindex, propertyname = _check_received_data(skicall, 'settext')
    # get set of element names for this property
    names = tools.elements(rconn, redisserver, devicename, propertyname)
    if not names:
        raise FailPage("Error parsing data")
    # initially set all element text values to be empty
    valuedict = {nm:'' for nm in names}
    received_data = skicall.submit_dict['received_data']
    if (propertyindex, 'tvtexttable', 'inputdict') in received_data:
        value = received_data[propertyindex, 'tvtexttable', 'inputdict'] # dictionary of names:values submitted
        for nm, vl in value.items():
            if nm in valuedict:
                valuedict[nm] = vl
            else:
                raise FailPage("Error parsing data")
        data_sent = tools.newtextvector(rconn, redisserver, devicename, propertyname, valuedict)
        print(data_sent)
        if not data_sent:
            raise FailPage("Error sending data")
    else:
        skicall.call_data["status"] = "Unable to parse received data"
        return
    set_state(skicall, sectionindex, "Busy")
    skicall.call_data["status"] = f"Change to property {propertyname} has been submitted"



def set_number(skicall):
    "Responds to a submission to set a number vector"
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    devicename, propertyindex, sectionindex, propertyname = _check_received_data(skicall, 'setnumber')
    # get set of element names for this property
    names = tools.elements(rconn, redisserver, devicename, propertyname)
    if not names:
        raise FailPage("Error parsing data")
    # initially set all element number values to be empty
    valuedict = {nm:'' for nm in names}
    received_data = skicall.submit_dict['received_data']
    if (propertyindex, 'nvinputtable', 'inputdict') in received_data:
        value = received_data[propertyindex, 'nvinputtable', 'inputdict'] # dictionary of names:values submitted
        for nm, vl in value.items():
            if nm in valuedict:
                valuedict[nm] = vl
            else:
                raise FailPage("Error parsing data")
        data_sent = tools.newnumbervector(rconn, redisserver, devicename, propertyname, valuedict)
        print(data_sent)
        if not data_sent:
            raise FailPage("Error sending data")
    else:
        skicall.call_data["status"] = "Unable to parse received data"
        return
    set_state(skicall, sectionindex, "Busy")
    skicall.call_data["status"] = f"Change to property {propertyname} has been submitted"


