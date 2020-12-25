
from base64 import urlsafe_b64encode, urlsafe_b64decode

from pathlib import Path

import gzip

from skipole import FailPage

from indi_mr import tools

## hiddenfields are
#
# propertyname
# sectionindex

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
    names = tools.elements(rconn, redisserver, propertyname, devicename)
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
        data_sent = tools.newswitchvector(rconn, redisserver, propertyname, devicename, valuedict)
        # print(data_sent)
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
        data_sent = tools.newswitchvector(rconn, redisserver, propertyname, devicename, valuedict)
        # print(data_sent)
        if not data_sent:
            raise FailPage("Error sending data")
    else:
        skicall.call_data["status"] = "Unable to parse received data"
        return
    set_state(skicall, sectionindex, "Busy")
    skicall.call_data["status"] = f"Change to property {propertyname} has been submitted" 


# The Client must send all members of Number and Text vectors,
# or may send just the members that change for other types.

def set_text(skicall):
    "Responds to a submission to set a text vector"
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    devicename, propertyindex, sectionindex, propertyname = _check_received_data(skicall, 'settext')
    # get set of element names for this property
    names = tools.elements(rconn, redisserver, propertyname, devicename)
    if not names:
        raise FailPage("Error parsing data")
    # initially set all element text values to be empty
    valuedict = {nm:'' for nm in names}
    received_data = skicall.submit_dict['received_data']
    if (propertyindex, 'tvtexttable', 'inputdict') in received_data:
        value = received_data[propertyindex, 'tvtexttable', 'inputdict'] # dictionary of base64 encoded names:values submitted
        for safekey, vl in value.items():
            nm = _fromsafekey(safekey)
            if nm in valuedict:
                valuedict[nm] = vl
            else:
                raise FailPage("Error parsing data")
        data_sent = tools.newtextvector(rconn, redisserver, propertyname, devicename, valuedict)
        # print(data_sent)
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
    names = tools.elements(rconn, redisserver, propertyname, devicename)
    if not names:
        raise FailPage("Error parsing data")
    # initially set all element number values to be empty
    valuedict = {nm:'' for nm in names}
    received_data = skicall.submit_dict['received_data']
    if (propertyindex, 'nvinputtable', 'inputdict') in received_data:
        value = received_data[propertyindex, 'nvinputtable', 'inputdict'] # dictionary of base 64 encoded names:values submitted
        for safekey, vl in value.items():
            nm = _fromsafekey(safekey)
            if nm in valuedict:
                valuedict[nm] = vl
            else:
                raise FailPage("Error parsing data")
        data_sent = tools.newnumbervector(rconn, redisserver, propertyname, devicename, valuedict)
        # print(data_sent)
        if not data_sent:
            raise FailPage("Error sending data")
    else:
        skicall.call_data["status"] = "Unable to parse received data"
        return
    set_state(skicall, sectionindex, "Busy")
    skicall.call_data["status"] = f"Change to property {propertyname} has been submitted"


def up_number(skicall):
    "An arrow up has been pressed to increment a numeric value on the page only - but not yet to be submitted"
    if skicall.ident_data:
        devicename = skicall.call_data["device"]
    else:
        raise FailPage("Unknown device")

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]

    received_data = skicall.submit_dict['received_data']

    if len(received_data) != 2:
        raise FailPage("Unknown property")

    # example of  received_data
    #
    # {
    # ('property_10', 'nvinputtable', 'up_getfield1'): XXXXXXXXXXX,  safekey of propertyname, element index, elementname
    # ('property_10', 'nvinputtable', 'getfield3'): current value
    # }

    getfield1 = ''
    getfield3 = ''
    propertyindex = ''

    for key, value in received_data.items():
        if (len(key) != 3) or (key[1] != 'nvinputtable'):
            raise FailPage("Unknown property")
        if key[2] == 'up_getfield1':
            getfield1 = value
        elif key[2] == 'getfield3':
            getfield3 = value
        else:
            raise FailPage("Unknown element/value")
        if propertyindex:
            if propertyindex != key[0]:
                raise FailPage("Unknown element/value")
        else:
            propertyindex = key[0]

    if (not getfield1) or (not getfield3):
        raise FailPage("Unknown element/value")
    parts = _fromsafekey(getfield1).split("\n")
    if len(parts) != 3:
        raise FailPage("Unknown element/value")
    propertyname = parts[0]
    try:
        elementindex = int(parts[1])
    except:
        raise FailPage("Unknown element/value")
    elementname = parts[2]

    # convert numeric value to float
    fvalue = tools.number_to_float(getfield3)

    # get element properties -  a dictionary of element attributes for the given element, property and device
    element =  tools.elements_dict(rconn, redisserver, elementname, propertyname, devicename)
    if not element:
        raise FailPage("Unknown element/value")
    # get step and minimum/max
    step = element['float_step']
    if not step:
        raise FailPage("Invalid action")
    minimum = element['float_min']
    maximum = element['float_max']
    newval = fvalue + step
    if maximum > minimum:
        if newval > maximum:
            newval = maximum
    if newval < minimum:
        newval = minimum
    # get newval as a formatted string
    formatted_value = tools.format_number(newval, element['format'])

    # get elements sorted by label
    elements = tools.property_elements(rconn, redisserver, propertyname, devicename)
    enumber = len(elements)

    # hide or not the up down arrow keys
    up_hide = []
    down_hide = []
    # up down keys need to identify the element, and the current requested value
    inputdict = {}
    getfield3values = []

    for index in range(enumber):
        if index == elementindex:
            # This element is being changed
            if newval >= maximum:
                up_hide.append(True)
            else:
                up_hide.append(False)
            if newval <= minimum:
                down_hide.append(True)
            else:
                down_hide.append(False)
            getfield3values.append(formatted_value)
            inputdict[_safekey(elementname)] = formatted_value
        else:
            # This element is unchanged
            up_hide.append(None)
            down_hide.append(None)
            getfield3values.append(None)
            # elements[index] gives a dictionary of the element at this index position, sorted by label
            # and ['name'] gives it by name. Setting the inputdict value to None means no change
            inputdict[_safekey(elements[index]['name'])] = None
 
    skicall.page_data[propertyindex,'nvinputtable', 'inputdict'] = inputdict
    skicall.page_data[propertyindex,'nvinputtable', 'up_hide'] = up_hide
    skicall.page_data[propertyindex,'nvinputtable', 'down_hide'] = down_hide
    skicall.page_data[propertyindex,'nvinputtable', 'getfield3'] = getfield3values
    



def down_number(skicall):
    "An arrow down has been pressed to decrement a numeric value on the page only - but not yet to be submitted"
    if skicall.ident_data:
        devicename = skicall.call_data["device"]
    else:
        raise FailPage("Unknown device")

    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]

    received_data = skicall.submit_dict['received_data']

    if len(received_data) != 2:
        raise FailPage("Unknown property")

    # example of  received_data
    #
    # {
    # ('property_10', 'nvinputtable', 'down_getfield1'): XXXXXXXXXXX,  safekey of propertyname, element index, elementname
    # ('property_10', 'nvinputtable', 'getfield3'): current value
    # }

    getfield1 = ''
    getfield3 = ''
    propertyindex = ''

    for key, value in received_data.items():
        if (len(key) != 3) or (key[1] != 'nvinputtable'):
            raise FailPage("Unknown property")
        if key[2] == 'down_getfield1':
            getfield1 = value
        elif key[2] == 'getfield3':
            getfield3 = value
        else:
            raise FailPage("Unknown element/value")
        if propertyindex:
            if propertyindex != key[0]:
                raise FailPage("Unknown element/value")
        else:
            propertyindex = key[0]

    if (not getfield1) or (not getfield3):
        raise FailPage("Unknown element/value")
    parts = _fromsafekey(getfield1).split("\n")
    if len(parts) != 3:
        raise FailPage("Unknown element/value")
    propertyname = parts[0]
    try:
        elementindex = int(parts[1])
    except:
        raise FailPage("Unknown element/value")
    elementname = parts[2]

    # convert numeric value to float
    fvalue = tools.number_to_float(getfield3)

    # get element properties -  a dictionary of element attributes for the given element, property and device
    element =  tools.elements_dict(rconn, redisserver, elementname, propertyname, devicename)
    if not element:
        raise FailPage("Unknown element/value")
    # get step and minimum
    step = element['float_step']
    if not step:
        raise FailPage("Invalid action")
    minimum = element['float_min']
    maximum = element['float_max']
    newval = fvalue - step
    if maximum > minimum:
        if newval > maximum:
            newval = maximum
    if newval < minimum:
        newval = minimum
    # get newval as a formatted string
    formatted_value = tools.format_number(newval, element['format'])

    # get number of elements
    enumber = len(tools.elements(rconn, redisserver, propertyname, devicename))

    # hide or not the up down arrow keys, create lists with the right number of entries
    up_hide = [None] * enumber
    down_hide = [None] * enumber
    getfield3values = [None] * enumber

    # set this element to change, all others remain at None
    if newval >= maximum:
        up_hide[elementindex] = True
    else:
        up_hide[elementindex] = False
    if newval <= minimum:
        down_hide[elementindex] = True
    else:
        down_hide[elementindex] = False
    getfield3values[elementindex] = formatted_value

    skicall.page_data[propertyindex,'nvinputtable', 'up_hide'] = up_hide
    skicall.page_data[propertyindex,'nvinputtable', 'down_hide'] = down_hide
    skicall.page_data[propertyindex,'nvinputtable', 'getfield3'] = getfield3values
    

    
def toggle_blob(skicall):
    "toggles a blob vector between enabled, disabled"
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    if skicall.ident_data:
        devicename = skicall.call_data["device"]
    else:
        raise FailPage("Unknown device")
    received_data = skicall.submit_dict['received_data']

    # example of  received_data
    #
    # {
    # ('property_4', 'enableblob', 'get_field1'): XXXXXXXXXXX,  safekey of propertyname, Enable or Disable
    # }

    if len(received_data) != 1:
        raise FailPage("Invalid data")
    # get the key, value from the dictionary
    key,data = next(iter(received_data.items()))

    if (len(key) != 3) or (key[1] != 'enableblob'):
        raise FailPage("Invalid data")
    if key[2] != 'get_field1':
        raise FailPage("Invalid data")
    propertyindex = key[0]

    if not data:
        raise FailPage("Invalid data")
    parts = _fromsafekey(data).split("\n")
    if len(parts) != 2:
        raise FailPage("Invalid data")
    propertyname, instruction = parts

    if (instruction != "Enable") and (instruction != "Disable"):
        raise FailPage("Invalid data")

    if instruction == "Disable":
         # Instruction is to disable, so publish never to disable
        data_sent = tools.enableblob(rconn, redisserver, propertyname, devicename, "never")
        skicall.call_data["status"] = f"BLOB's can no longer be received for {propertyname} via the indiserver port"
        # set button text to "Enable"
        skicall.page_data[propertyindex, 'enableblob', 'button_text'] = "Enable"
        skicall.page_data[propertyindex, 'enableblob', 'get_field1'] = _safekey(propertyname + "\nEnable")
        skicall.page_data[propertyindex,'bvtable', 'col2'] = [ None, None, None, "Disabled"]
    else:
        # toggle to enabled
        data_sent = tools.enableblob(rconn, redisserver, propertyname, devicename, "also")
        skicall.call_data["status"] = f"BLOB's can now be received for {propertyname} via the indiserver port"
        # set button text to "Disable"
        skicall.page_data[propertyindex, 'enableblob', 'button_text'] = "Disable"
        skicall.page_data[propertyindex, 'enableblob', 'get_field1'] = _safekey(propertyname + "\nDisable")
        skicall.page_data[propertyindex,'bvtable', 'col2'] = [ None, None, None, "Enabled"]



def set_blob(skicall):
    "Responds to a submission to upload a blob"
    rconn = skicall.proj_data["rconn"]
    redisserver = skicall.proj_data["redisserver"]
    # device name should already be set in ident_data with skicall.call_data["device"]
    rxdata = skicall.call_data['upblob', 'hidden_field1']
    data = _fromsafekey(rxdata)
    propertyname, sectionindex, elementname = data.split("\n")
    devicename = skicall.call_data["device"]
    rxfile = skicall.call_data['upblob', "action"]
    lenrxfile = len(rxfile)
    fpath = skicall.call_data['upblob', "submitbutton"]
    fextension = Path(fpath).suffixes    #  fextension is something like ['.tar'] or ['tar', '.gz']
    fext = ''
    for f in fextension:
        fext += f
    if skicall.call_data['zipbox', "checkbox"] == "zipfile":
        # zip the file and add .gz extension
        rxfile = gzip.compress(rxfile)
        fext = fext + ".gz"
    data_sent = tools.newblobvector(rconn, redisserver, propertyname, devicename, [{'name':elementname, 'size':lenrxfile, 'format':fext, 'value':rxfile}])
    if not data_sent:
        raise FailPage("Error sending data")
    set_state(skicall, sectionindex, "Busy")
    skicall.call_data["status"] = f"""The file has been submitted:
    Device name   : {devicename}
    Property name : {propertyname}
    Element name  : {elementname}
    Size          : {lenrxfile}
    Format        : {fext}"""





