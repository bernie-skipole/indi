

###################
#
#  fromxml
#
###################


"""Reads indi xml strings, parses them and places values into redis,
ready for reading by the web server."""


import xml.etree.ElementTree as ET

import math, json

from datetime import datetime

from base64 import standard_b64decode, standard_b64encode


########## redis keys and channels

_KEYPREFIX = ""
_TO_INDI_CHANNEL = ""
_FROM_INDI_CHANNEL = ""


#   redis keys and data
#
#   one key : set
#   'devices' - set of device names   ('devices' is a literal string)

#   multiple keys : sets
#   'properties:<devicename>' - set of property names for the device ('properties' is a literal string
#                                                                     <devicename> is an actual device name)

#   multiple keys : hash tables ( python dictionaries )
#   'attributes:<propertyname>:<devicename>' - dictionary of attributes for the property ('attributes' is a literal string
#                                                                                         <propertyname> is an actual property name
#                                                                                         <devicename> is an actual device name

#   one key : list
#   'messages' - list of "Timestamp space message"

#   multiple keys : lists
#   'devicemessages:<devicename>' - list of "Timestamp space message"


#   multiple keys : sets
#   'elements:<propertyname>:<devicename>' - set of element names for the device property
#                                             ('elements' is a literal string
#                                              <propertyname> is an actual property name
#                                              <devicename> is an actual device name)


#   multiple keys : hash tables ( python dictionaries )
#   'elementattributes:<elementname>:<propertyname>:<devicename>' - dictionary of attributes for the element
#                                                                   ('elementattributes' is a literal string
#                                                                    <elementname> is an actual element name
#                                                                    <propertyname> is an actual property name
#                                                                    <devicename> is an actual device name)




_LOGLENGTHS = {
                'devices' : 5,
                'properties' : 5,
                'attributes' : 5,
                'elements': 5,
                'messages': 5,
                'textvector': 5,
                'numbervector':50,
                'switchvector':5,
                'lightvector':5,
                'blobvector':5
              }



def receive_from_indiserver(data, rconn):
    "receives xml data, parses it and stores in redis. Publishes an alert that data is received"
    if rconn is None:
        return
    # this timestamp is the time at which the data is received
    timestamp = datetime.utcnow().isoformat(sep='T')
    # data comes in block of xml elements, not inside a root, so create a root
    # element 'commsroot'
    xmlstring = b"".join((b"<commsroot>", data, b"</commsroot>"))
    root = ET.fromstring(xmlstring)
    for child in root:
        if child.tag == "defTextVector":
            text_vector = TextVector(child)         # store the received data in a TextVector object
            text_vector.write(rconn)                # call the write method to store data in redis
            text_vector.log(rconn, timestamp)
        elif child.tag == "defNumberVector":
            number_vector = NumberVector(child)
            number_vector.write(rconn)
            number_vector.log(rconn, timestamp)
        elif child.tag == "defSwitchVector":
            switch_vector = SwitchVector(child)
            switch_vector.write(rconn)
            switch_vector.log(rconn, timestamp)
        elif child.tag == "defLightVector":
            light_vector = LightVector(child)
            light_vector.write(rconn)
            light_vector.log(rconn, timestamp)
        elif child.tag == "defBLOBVector":
            blob_vector = BLOBVector(child)
            blob_vector.write(rconn)
            blob_vector.log(rconn, timestamp)
        elif child.tag == "message":
            message = Message(child)
            message.write(rconn)
            message.log(rconn, timestamp)
        elif child.tag == "delProperty":
            delprop = delProperty(child)
            delprop.write(rconn)
            delprop.log(rconn, timestamp)
        elif child.tag == "setTextVector":
            text_vector = TextVector.update_from_setvector(rconn, child)
            text_vector.log(rconn, timestamp)
        elif child.tag == "setNumberVector":
            number_vector = NumberVector.update_from_setvector(rconn, child)
            number_vector.log(rconn, timestamp)
        elif child.tag == "setSwitchVector":
            switch_vector = SwitchVector.update_from_setvector(rconn, child)
            switch_vector.log(rconn, timestamp)
        elif child.tag == "setLightVector":
            light_vector = LightVector.update_from_setvector(rconn, child)
            light_vector.log(rconn, timestamp)
        elif child.tag == "setBLOBVector":
            blob_vector = BLOBVector.update_from_setvector(rconn, child)
            blob_vector.log(rconn, timestamp)


def setup_redis(key_prefix, to_indi_channel, from_indi_channel):
    "Sets the redis key prefix and pubsub channels"
    global _KEYPREFIX, _TO_INDI_CHANNEL, _FROM_INDI_CHANNEL
    if key_prefix:
        _KEYPREFIX = key_prefix
    else:
        _KEYPREFIX = ""
    if to_indi_channel:
        _TO_INDI_CHANNEL = to_indi_channel
    else:
        _TO_INDI_CHANNEL = ""
    if from_indi_channel:
        _FROM_INDI_CHANNEL = from_indi_channel
    else:
        _FROM_INDI_CHANNEL = ""


def get_to_indi_channel():
    return _TO_INDI_CHANNEL

def get_from_indi_channel():
    return _FROM_INDI_CHANNEL


def key(*keys):
    "Add the prefix to keys, delimit keys with :"
    # example - if keys are 'device', 'property' this will result in a key of
    # 'keyprefixdevice:property'
    return _KEYPREFIX + ":".join(keys)



############# Define properties



class ParentProperty():

    "Parent to Text, Number, Switch, Lights, Blob vectors"

    def __init__(self, vector):
        "Parent Item"
        # Required properties
        self.device = vector.get("device")    # name of Device
        self.name = vector.get("name")        # name of Property
        # state case may be incorrect (some confusion in white paper over the case of 'Ok')
        state = vector.get("state").lower()      # current state of Property should be one of Idle, Ok, Busy or Alert
        if state == "idle":
            self.state = "Idle"
        elif state == "ok":
            self.state = "Ok"
        elif state == "busy":
            self.state = "Busy"
        else:
            self.state = "Alert"
        # implied properties
        self.label = vector.get("label", default = self.name)                             # GUI label, use name by default
        self.group = vector.get("group", default = "")                                    # Property group membership, blank by default
        self.timestamp = vector.get("timestamp", default = datetime.utcnow().isoformat()) # moment when these data were valid
        self.message = vector.get("message", default = "")

        # add the class name so it is saved with attributes to redis, so the type of vector can be read
        self.vector = self.__class__.__name__
        # self.elements is a dictionary which will hold the elements within this vector, keys are element names
        self.elements = {}


    def _set_permission(self, permission):
        "Sets the possible permissions, Read-Only, Write-Only or Read-Write"
        if permission in ('ro', 'wo', 'rw'):
            self.perm = permission
        else:
            self.perm = 'ro'


    @classmethod
    def get_devices(cls, rconn):
        "Return a set of device names as saved in redis"
        deviceset = rconn.smembers(key('devices'))
        if not deviceset:
            return set()
        return set(d.decode("utf-8") for d in deviceset)

    def get_properties(self, rconn):
        "Returns a set of property names for this device as saved in redis"
        propertyset = rconn.smembers(key('properties', self.device))
        if not propertyset:
            return set()
        return set(p.decode("utf-8") for p in propertyset)

    def get_attributes(self, rconn):
        "Returns a dictionary of attributes for this property and device as saved in redis"
        attdict = rconn.hgetall(key('attributes',self.name,self.device))
        if not attdict:
            return {}
        return {k.decode("utf-8"):v.decode("utf-8") for k,v in attdict.items()}

    def get_elements(self, rconn):
        "Returns a set of element names for this device as saved in redis"
        elementset = rconn.smembers(key('elements',self.name,self.device))
        if not elementset:
            return set()
        return set(e.decode("utf-8") for e in elementset)


    def get_elements_dict(self, rconn, elementname):
        "Returns a dictionary of element attributes for the given element name, as saved in redis"
        elkey = key("elementattributes", elementname, self.name, self.device)
        eldict = rconn.hgetall(elkey)
        if not eldict:
            return {}
        return {k.decode("utf-8"):v.decode("utf-8") for k,v in eldict.items()}


    def write(self, rconn):
        "Saves this device, and property to redis connection rconn"
        # add the device to redis set 'devices'
        rconn.sadd(key('devices'), self.device)                 # add device to 'devices'
        rconn.sadd(key('properties', self.device), self.name)   # add property name to 'properties:<devicename>'
        # Saves the instance attributes to redis, apart from self.elements
        mapping = {key:value for key,value in self.__dict__.items() if key != "elements"}
        rconn.hmset(key('attributes',self.name,self.device), mapping)
        # save list of element names
        # get list of element names sorted by label
        elementlist = list(self.elements.keys())
        elementlist.sort(key=lambda x: self.elements[x].label)
        for elementname in elementlist:
            rconn.sadd(key('elements', self.name, self.device), elementname)   # add element name to 'elements:<propertyname>:<devicename>'


    def log(self, rconn, timestamp):
        "Reads last log entry in redis for this object, and, if changed, logs change with the given timestamp"
        global _LOGLENGTHS
        # log changes in devices to logdata:devices
        deviceset = self.get_devices(rconn)
        logkey = key("logdata", "devices")
        logentry = rconn.lindex(logkey, 0)   # gets last log entry
        if logentry is None:
            newstring = timestamp + " " + json.dumps(list(deviceset))
            rconn.lpush(logkey, newstring)
        else:
            # Get the last log
            logtime, logdevices = logentry.decode("utf-8").split(" ", maxsplit=1)  # decode b"timestamp json_string_of_devices_list"
            logdeviceset = set(json.loads(logdevices))
            if logdeviceset != deviceset:
                # there has been a change in the devices
                newstring = timestamp + " " + json.dumps(list(deviceset))
                rconn.lpush(logkey, newstring)
                # and limit number of logs
                rconn.ltrim(logkey, 0, _LOGLENGTHS['devices'])
        # log changes in property names to logdata:properties:<devicename>
        propertyset = self.get_properties(rconn)
        logkey = key("logdata", 'properties', self.device)
        logentry = rconn.lindex(logkey, 0)   # gets last log entry
        if logentry is None:
            newstring = timestamp + " " + json.dumps(list(propertyset))
            rconn.lpush(logkey, newstring)
        else:
            # Get the last log
            logtime, logproperties = logentry.decode("utf-8").split(" ", maxsplit=1)  # decode b"timestamp json_string_of_properties_list"
            logpropertyset = set(json.loads(logproperties))
            if logpropertyset != propertyset:
                # there has been a change in the properties
                newstring = timestamp + " " + json.dumps(list(propertyset))
                rconn.lpush(logkey, newstring)
                # and limit number of logs
                rconn.ltrim(logkey, 0, _LOGLENGTHS['properties'])
        # log changes in attributes to logdata:attributes:<propertyname>:<devicename>
        attdict = self.get_attributes(rconn)
        logkey = key("logdata", 'attributes',self.name,self.device)
        logentry = rconn.lindex(logkey, 0)   # gets last log entry
        if logentry is None:
            newstring = timestamp + " " + json.dumps(attdict)
            rconn.lpush(logkey, newstring)
        else:
            # Get the last log
            logtime, logattributes = logentry.decode("utf-8").split(" ", maxsplit=1)  # decode b"timestamp json_string_of_attributes_dict"
            logattdict = json.loads(logattributes)
            if logattdict != attdict:
                # there has been a change in the attributes
                newstring = timestamp + " " + json.dumps(attdict)
                rconn.lpush(logkey, newstring)
                # and limit number of logs
                rconn.ltrim(logkey, 0, _LOGLENGTHS['attributes'])
        # log changes in element names to logdata:elements:<propertyname>:<devicename>
        elementset = self.get_elements(rconn)
        logkey = key("logdata", 'elements',self.name,self.device)
        logentry = rconn.lindex(logkey, 0)   # gets last log entry
        if logentry is None:
            newstring = timestamp + " " + json.dumps(list(elementset))
            rconn.lpush(logkey, newstring)
        else:
            # Get the last log
            logtime, logelements = logentry.decode("utf-8").split(" ", maxsplit=1)  # decode b"timestamp json_string_of_elements_list"
            logelementset = set(json.loads(logelements))
            if logelementset != elementset:
                # there has been a change in the elements
                newstring = timestamp + " " + json.dumps(list(elementset))
                rconn.lpush(logkey, newstring)
                # and limit number of logs
                rconn.ltrim(logkey, 0, _LOGLENGTHS['elements'])
        # log changes in element attributes
        for element in self.elements.values():
            # log changes in attributes to logdata:elementattributes:<elementname>:<propertyname>:<devicename>
            elattdict = self.get_elements_dict(rconn, element.name)
            logkey = key("logdata", 'elementattributes',element.name, self.name, self.device)
            logentry = rconn.lindex(logkey, 0)   # gets last log entry
            if logentry is None:
                newstring = timestamp + " " + json.dumps(elattdict)
                rconn.lpush(logkey, newstring)
            else:
                # Get the last log
                logtime, logelattributes = logentry.decode("utf-8").split(" ", maxsplit=1)  # decode b"timestamp json_string_of_element_attributes_dict"
                logelattdict = json.loads(logelattributes)
                if logelattdict != elattdict:
                    # there has been a change in the element attributes
                    newstring = timestamp + " " + json.dumps(elattdict)
                    rconn.lpush(logkey, newstring)
                    # and limit number of logs
                    rconn.ltrim(logkey, 0, _LOGLENGTHS[self.vector.lower()])



    @classmethod
    def read(cls, rconn, device, name):
        """Reads redis and returns an instance of this class"""
        # If device is not in the 'devices' set, return None
        if not rconn.sismember(key('devices'), device):
            return
        # If the property name is not recognised as a property of the device, return None
        if not rconn.sismember(key('properties', device), name):
            return
        # create a _XMLVector object to simulate an XML element
        xmlvector = _XMLVector(rconn, device, name)
        # and use it to return an instance of this class
        return cls(xmlvector)


    def update(self, rconn, vector):
        "Update the object attributes to redis"
        # alter self according to the values to be set
        state = vector.get("state")     # set state of Property; Idle, OK, Busy or Alert, no change if absent
        if state:
            self.state = state
        self.timestamp = vector.get("timestamp", default = datetime.utcnow().isoformat()) # moment when these data were valid
        self.message = vector.get("message", default = "")
        # Saves the instance attributes to redis, apart from self.elements
        mapping = {key:value for key,value in self.__dict__.items() if key != "elements"}
        rconn.hmset(key('attributes',self.name,self.device), mapping)


    @classmethod
    def update_from_setvector(cls, rconn, setvector):
        """Gets an instance of this class from redis, and updates it
           according to the instructions from the setvector
           Returns an updated instance of this class or None if unable to read the property"""
        device = setvector.get("device")
        if device is None:
            return
        name = setvector.get("name")
        if name is None:
            return
        # Create an instance of the class, by reading the property from redis
        currentvector = cls.read(rconn, device, name)
        if currentvector is None:
            # device or property is unknown
            return
        # call the update method of the property, this writes changes to redis
        currentvector.update(rconn, setvector)
        return currentvector


    def element_names(self):
        "Returns a list of element names"
        return list(self.elements.keys())


    def __getitem__(self, key):
        "key is an element name, returns an element object"
        return self.elements[key]


    def __setitem__(self, key, value):
        "key is an element name, value is an element"
        if key != value.name:
            raise ValueError("The key should be equal to the name set in the element")
        self.elements[key] = value


    def __contains__(self, name):
        "Check if an element with this name is in the vector"
        return name in self.elements


    def __iter__(self):
        "Iterating over the property gives the elements"
        for element in self.elements.values():
            yield element


    def __str__(self):
        "Creates a string of label:states"
        if not self.elements:
            return ""
        result = ""
        for element in self.elements.values():
            result += element.label + " : " + str(element)+"\n"
        return result



class ParentElement():
    "Parent to Text, Number, Switch, Lights, Blob elements"

    def __init__(self, child):
        self.name = child.get("name")                       # name of the element, required value
        self.label = child.get("label", default=self.name)  # GUI label, use name by default




################ Text ######################

class TextVector(ParentProperty):

    def __init__(self, vector):
        "The vector is the xml defTextVector element or an _XMLVector instance"
        super().__init__(vector)
        perm = vector.get("perm")
        self._set_permission(perm)                 # ostensible Client controlability
        self.timeout = vector.get("timeout", default = 0)   # worse-case time to affect, 0 default, N/A for ro
        for child in vector:
            element = TextElement(child)
            self.elements[element.name] = element


    def write(self, rconn):
        "Saves name, label, value in 'elementattributes:<elementname>:<propertyname>:<devicename>'"
        for element in self.elements.values():
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), element.__dict__)
        super().write(rconn)


    def update(self, rconn, vector):
        "Update the object attributes and changed elements to redis"
        self.timeout = vector.get("timeout", default = 0)
        for child in vector:
            element = self.elements[child.get("name")]
            element.set_value(child)   # change its value to that given by the xml child
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), element.__dict__)
        super().update(rconn, vector)


class TextElement(ParentElement):
    "text elements contained in a TextVector"

    def __init__(self, child):
        self.set_value(child)
        super().__init__(child)

    def set_value(self, child):
        if (child is None) or (not child.text):
            self.value = ""
        else:
            self.value = child.text.strip()       # remove any newlines around the xml text

    def __str__(self):
        return self.value



################ Number ######################

class NumberVector(ParentProperty):


    def __init__(self, vector):
        "The vector is the defNumberVector element or an _XMLVector instance"
        super().__init__(vector)
        perm = vector.get("perm")
        self._set_permission(perm)                 # ostensible Client controlability
        self.timeout = vector.get("timeout", default = 0)   # worse-case time to affect, 0 default, N/A for ro
        for child in vector:
            element = NumberElement(child)
            self.elements[element.name] = element

    def write(self, rconn):
        "Saves name, label, format, min, max, step, value, formatted_number in 'elementattributes:<elementname>:<propertyname>:<devicename>'"
        for element in self.elements.values():
            mapping = {key:value for key,value in element.__dict__.items()}
            mapping["formatted_number"] = element.formatted_number()
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), mapping)
        super().write(rconn)


    def update(self, rconn, vector):
        "Update the object attributes and changed elements to redis"
        self.timeout = vector.get("timeout", default = 0)
        for child in vector:
            element = self.elements[child.get("name")]
            element.set_value(child)   # change its value to that given by the xml child
            mapping = {key:value for key,value in element.__dict__.items()}
            mapping["formatted_number"] = element.formatted_number()
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), mapping)
        super().update(rconn, vector)



class NumberElement(ParentElement):
    "number elements contained in a NumberVector"

    def __init__(self, child):
        # required number attributes
        self.format = child.get("format")    # printf-style format for GUI display
        self.min = child.get("min")          # minimal value
        self.max = child.get("max")           # maximum value, ignore if min == max
        self.step = child.get("step")        # allowed increments, ignore if 0
        # get the raw self.value
        self.set_value(child)
        super().__init__(child)

    def set_value(self, child):
        if child.text is None:
            self.value = ""
        else:
            self.value = child.text.strip()       # remove any newlines around the xml text


    def formatted_number(self):
        """Returns the string of the number using the format value"""
        # Splits the number into a negative flag and three sexagesimal parts
        # then calls self._sexagesimal or self._printf to create the formatted string
        value = self.value
        # negative is True, if the value is negative
        negative = value.startswith("-")
        if negative:
            value = value.lstrip("-")
        # Is the number provided in sexagesimal form?
        if " " in value:
            parts = value.split(" ")
        elif ":" in value:
            parts = value.split(":")
        elif ";" in value:
            parts = value.split(";")
        else:
            # not sexagesimal
            parts = [value, "0", "0"]
        # Any missing parts should have zero
        if len(parts) == 2:
            # assume seconds are missing, set to zero
            parts.append("0")
        assert len(parts) == 3
        number_strings = list(x if x else "0" for x in parts)
        # convert strings to integers or floats
        number_list = []
        for part in number_strings:
            try:
                num = int(part)
            except ValueError:
                num = float(part)
            number_list.append(num)
        # convert the number to a formatted string
        if self.format.startswith("%") and self.format.endswith("m"):
            return self._sexagesimal(negative, number_list)
        else:
            return self._printf(negative, number_list)


    def _sexagesimal(self, negative, number_list):
        "Create string of the number according to the given format"
        # degrees and minutes should be integers
        if not isinstance(number_list[0], int):
            # its a float, so get integer part and fraction part
            fractdegrees, degrees = math.modf(number_list[0])
            number_list[0] = int(degrees)
            number_list[1] += 60*fractdegrees
        if not isinstance(number_list[1], int):
            # its a float, so get integer part and fraction part
            fractminutes, minutes = math.modf(number_list[1])
            number_list[1] = int(minutes)
            number_list[2] += 60*fractminutes
        # Ensure minutes and seconds are less than 60
        minutes = 0        
        while number_list[2] >= 60:
            number_list[2] -= 60
            minutes += 1
        number_list[1] += minutes
        degrees = 0
        while number_list[1] >= 60:
            number_list[1] -= 60
            degrees += 1
        number_list[0] += degrees

        # so number list is a valid degrees, minutes, seconds

        # degrees
        if negative:
            number = f"-{number_list[0]}:"
        else:
            number = f"{number_list[0]}:"

        # format string is of the form  %<w>.<f>m
        w,f = self.format.split(".")
        w = w.lstrip("%")
        f = f.rstrip("m")

        if (f == "3") or (f == "5"):
            # no seconds, so create minutes value
            minutes = float(number_list[1]) + number_list[2]/60.0
            if f == "5":
                number += f"{minutes:04.1f}"
            else:
                number += f"{minutes:02.0f}"
        else:
            number += f"{number_list[1]:02d}:"
            seconds = float(number_list[2])
            if f == "6":
                number += f"{seconds:02.0f}"
            elif f == "8":
                number += f"{seconds:04.1f}"
            else:
                number += f"{seconds:05.2f}"

        # w is the overall length of the string, prepend with spaces to make the length up to w
        w = int(w)
        l = len(number)
        if w>l:
            number = " "*(w-l) + number

        return number


    def _printf(self, negative, number_list):
        "Create string of the number according to the given format"
        value = number_list[0] + (number_list[1]/60) + (number_list[2]/360)
        if negative:
            value = -1 * value
        return self.format % value


    def __str__(self):
        "Returns the formatted number, equivalent to self.formatted_number()"
        return self.formatted_number()


################ Switch ######################

class SwitchVector(ParentProperty):

    def __init__(self, vector):
        "The vector is the xml defSwitchVector element or an _XMLVector instance"
        super().__init__(vector)
        perm = vector.get("perm")
        self._set_permission(perm)                          # ostensible Client controlability
        self.rule = vector.get("rule")                      # hint for GUI presentation (OneOfMany|AtMostOne|AnyOfMany)
        self.timeout = vector.get("timeout", default = 0)   # worse-case time to affect, 0 default, N/A for ro
        for child in vector:
            element = SwitchElement(child)
            self.elements[element.name] = element


    def write(self, rconn):
        "Saves name, label, value in 'elementattributes:<elementname>:<propertyname>:<devicename>'"
        for element in self.elements.values():
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), element.__dict__)
        super().write(rconn)


    def update(self, rconn, vector):
        "Update the object attributes and changed elements to redis"
        self.timeout = vector.get("timeout", default = 0)
        for child in vector:
            element = self.elements[child.get("name")]
            element.set_value(child)   # change its value to that given by the xml child
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), element.__dict__)
        super().update(rconn, vector)



    def _set_permission(self, permission):
        "Sets the possible permissions, Read-Only or Read-Write"
        if permission in ('ro', 'rw'):
            self.perm = permission
        else:
            self.perm = 'ro'



class SwitchElement(ParentElement):
    "switch elements contained in a SwitchVector"

    def __init__(self, child):
        "value should be Off or On"
        self.set_value(child)
        super().__init__(child)

    def set_value(self, child):
        if child.text is None:
            self.value = ""
        else:
            self.value = child.text.strip()       # remove any newlines around the xml text


    def __str__(self):
        return self.value



################ Lights ######################

class LightVector(ParentProperty):


    def __init__(self, vector):
        "The vector is the defLightVector element or an _XMLVector instance"
        super().__init__(vector)
        self.perm = 'ro'                      # permission always Read-Only
        for child in vector:
            element = LightElement(child)
            self.elements[element.name] = element


    def update(self, rconn, vector):
        "Update the object attributes and changed elements to redis"
        for child in vector:
            element = self.elements[child.get("name")]
            element.set_value(child)   # change its value to that given by the xml child
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), element.__dict__)
        super().update(rconn, vector)


    def write(self, rconn):
        "Saves name, label, value in 'elementattributes:<elementname>:<propertyname>:<devicename>'"
        for element in self.elements.values():
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), element.__dict__)
        super().write(rconn)


class LightElement(ParentElement):
    "light elements contained in a LightVector"

    def __init__(self, child):
        self.set_value(child)
        super().__init__(child)

    def set_value(self, child):
        if child.text is None:
            self.value = ""
        else:
            self.value = child.text.strip()       # remove any newlines around the xml text

    def __str__(self):
        return self.value


        

################ BLOB ######################

class BLOBVector(ParentProperty):

    def __init__(self, vector):
        "The vector is the defBLOBVector element or an _XMLVector instance"
        super().__init__(vector)
        perm = vector.get("perm")
        self._set_permission(perm)                          # ostensible Client controlability
        self.timeout = vector.get("timeout", default = 0)   # worse-case time to affect, 0 default, N/A for ro
        for child in vector:
            element = BLOBElement(child)
            self.elements[element.name] = element


    def update(self, rconn, vector):
        "Update the object attributes and changed elements to redis"
        self.timeout = vector.get("timeout", default = 0)
        for child in vector:
            element = self.elements[child.get("name")]
            element.size = child.get("size")     # number of bytes in decoded and uncompressed BLOB
            element.format = child.get("format") # format as a file suffix, eg: .z, .fits, .fits.z
            element.set_value(child)   # change its value to that given by the xml child
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), element.__dict__)
        super().update(rconn, vector)


    def write(self, rconn):
        "Saves name, label, value in 'elementattributes:<elementname>:<propertyname>:<devicename>'"
        for element in self.elements.values():
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), element.__dict__)
        super().write(rconn)

    def __str__(self):
        "Creates a string of labels"
        if not self.elements:
            return ""
        result = ""
        for element in self.elements.values():
            result += element.label + "\n"
        return result


class BLOBElement(ParentElement):
    "BLOB elements contained in a BLOBVector"


    def __init__(self, child):
        "value is a binary value"
        self.size =  child.get("size", default = "")     # number of bytes in decoded and uncompressed BLOB
        self.format =  child.get("format", default = "") # format as a file suffix, eg: .z, .fits, .fits.z
        self.set_value(child)
        super().__init__(child)


    def set_value(self, child):
        if child.text is None:
            self.value = b""
        else:
            self.value = standard_b64decode(child.text)   ## decode from base64

    def __str__(self):
        return ""



################ Message ####################


class Message():
    "a message associated with a device or entire system"

    def __init__(self, child):
        self.device = child.get("device", default = "")                                  # considered to be site-wide if absent
        self.timestamp = child.get("timestamp", default = datetime.utcnow().isoformat()) # moment when this message was generated
        self.message = child.get("message", default = "")                                # Received message


    @classmethod
    def get_message(cls, rconn, device=""):
        """Return the last message as list of [timestamp, message] or [] if not available
           If device not given, return the last system message
           If device given, the last message from this device is returned"""
        if device:
            mkey = key("devicemessages", device)
        else:
            mkey = key("messages")
        message = rconn.get(mkey)
        if message is None:
            return []
        return message.decode("utf-8").split(" ", maxsplit=1)  # decode b"timestamp message"

    def write(self, rconn):
        "Saves this message as a string, 'timestamp message'"
        if not self.message:
            return
        time_and_message = self.timestamp + " " + self.message
        if self.device:
            rconn.set(key('devicemessages', self.device), time_and_message)
        else:
            rconn.set(key('messages'), time_and_message)


    def log(self, rconn, timestamp):
        "Reads last log entry in redis for this object, and, if changed, logs change with the given timestamp"
        global _LOGLENGTHS
        # log changes in messages to logdata:messages or to logdata:devicemessages:<devicename>
        messagelist = self.get_message(rconn, device=self.device)
        if not messagelist:
            return
        if self.device:
            logkey = key("logdata", "devicemessages", self.device)
        else:
            logkey = key("logdata", "messages")
        logentry = rconn.lindex(logkey, 0)   # gets last log entry
        if logentry is None:
            newstring = timestamp + " " + json.dumps(messagelist)
            rconn.lpush(logkey, newstring)
        else:
            # Get the last log
            logtime, logmessage = logentry.decode("utf-8").split(" ", maxsplit=1)  # decode b"timestamp json_string_of_[timestamp message]"
            logmessagelist = json.loads(logmessage)
            if logmessagelist != messagelist:
                # there has been a change in the message
                newstring = timestamp + " " + json.dumps(messagelist)
                rconn.lpush(logkey, newstring)
                # and limit number of logs
                rconn.ltrim(logkey, 0, _LOGLENGTHS['messages'])

    def __str__(self):
        return self.message


################## Deleting #####################


class delProperty():

# A Device may tell a Client a given Property is no longer available by sending delProperty. If the command specifies only a
# Device without a Property, the Client must assume all the Properties for that Device, and indeed the Device itself, are no
# longer available.

    def __init__(self, child):
        "Delete the given property, or device if property name is None"
        self.device = child.get("device")
        self.name = child.get("name", default = "")
        self.timestamp = child.get("timestamp", default = datetime.utcnow().isoformat()) # moment when this message was generated
        self.message = child.get("message", default = "")                                # Received message


    def write(self, rconn):
        "Deletes the property or device from redis"
        global _LOGLENGTHS
        if self.name:
            # delete the property and add the message to the device message
            if self.message:
                time_and_message = f"{self.timestamp} {self.message}"
            else:
                time_and_message = f"{self.timestamp} Property {self.name} deleted from device {self.device}"
            rconn.set(key('messages', self.device), time_and_message)
            # delete all elements associated with the property
            elements = rconn.smembers(key('elements', self.name, self.device))
            # delete the set of elements for this property
            rconn.delete(key('elements', self.name, self.device))
            element_names = list(en.decode("utf-8") for en in elements)
            for name in element_names:
                # delete the element attributes
                rconn.delete(key('elementattributes', name, self.name, self.device))
            # and delete the property
            rconn.srem(key('properties', self.device), self.name)
            rconn.delete(key('attributes', self.name, self.device))
        else:
            # delete the device and add the message to the system message
            if self.message:
                time_and_message = f"{self.timestamp} {self.message}"
            else:
                time_and_message = f"{self.timestamp} {self.device} deleted"
            rconn.set(key('messages'), time_and_message)
            # and delete all keys associated with the device
            properties = rconn.smembers(key('properties', self.device))
            # delete the set of properties
            rconn.delete(key('properties', self.device))
            property_names = list(pn.decode("utf-8") for pn in properties)
            for name in property_names:
                # delete all elements associated with the property
                elements = rconn.smembers(key('elements', name, self.device))
                # delete the set of elements for this property
                rconn.delete(key('elements', name, self.device))
                element_names = list(en.decode("utf-8") for en in elements)
                for ename in element_names:
                    # delete the element attributes
                    rconn.delete(key('elementattributes', ename, name, self.device))
                # delete the properties attributes
                rconn.delete(key('attributes', name, self.device))
            # delete messages associated with the device
            rconn.delete(key('messages', self.device))
            # delete the device from the 'devices' set
            rconn.srem(key('devices'), self.device)

    def log(self, rconn, timestamp):
        "Reads last log entry in redis for this object, and, if changed, logs change with the given timestamp"
        global _LOGLENGTHS
        if self.name:
            # a property has been deleted, log changes in property names to logdata:properties:<devicename>
            propertysetfromredis = rconn.smembers(key('properties', self.device))
            if not propertysetfromredis:
                propertyset = set(["--None--"])
            else:
                propertyset = set(p.decode("utf-8") for p in propertysetfromredis)
            logkey = key("logdata", 'properties', self.device)
            logentry = rconn.lindex(logkey, 0)   # gets last log entry
            if logentry is None:
                newstring = timestamp + " " + json.dumps(list(propertyset))
                rconn.lpush(logkey, newstring)
            else:
                # Get the last log
                logtime, logproperties = logentry.decode("utf-8").split(" ", maxsplit=1)  # decode b"timestamp json_string_of_properties_list"
                logpropertyset = set(json.loads(logproperties))
                if logpropertyset != propertyset:
                    # there has been a change in the properties
                    newstring = timestamp + " " + json.dumps(list(propertyset))
                    rconn.lpush(logkey, newstring)
                    # and limit number of logs
                    rconn.ltrim(logkey, 0, _LOGLENGTHS['properties'])
            # log changes in messages to logdata:devicemessages:<devicename>
            messagelist = Message.get_message(rconn, device=self.device)
            if not messagelist:
                return
            logkey = key("logdata", "devicemessages", self.device)
            logentry = rconn.lindex(logkey, 0)   # gets last log entry
            if logentry is None:
                newstring = timestamp + " " + json.dumps(messagelist)
                rconn.lpush(logkey, newstring)
            else:
                # Get the last log
                logtime, logmessage = logentry.decode("utf-8").split(" ", maxsplit=1)  # decode b"timestamp json_string_of_[timestamp message]"
                logmessagelist = json.loads(logmessage)
                if logmessagelist != messagelist:
                    # there has been a change in the message
                    newstring = timestamp + " " + json.dumps(messagelist)
                    rconn.lpush(logkey, newstring)
                    # and limit number of logs
                    rconn.ltrim(logkey, 0, _LOGLENGTHS['messages'])
        else:
            # no property name, so an entire device has been wiped
            # log changes in devices to logdata:devices
            deviceset = ParentProperty.get_devices(rconn)
            logkey = key("logdata", "devices")
            logentry = rconn.lindex(logkey, 0)   # gets last log entry
            if logentry is None:
                newstring = timestamp + " " + json.dumps(list(deviceset))
                rconn.lpush(logkey, newstring)
            else:
                # Get the last log
                logtime, logdevices = logentry.decode("utf-8").split(" ", maxsplit=1)  # decode b"timestamp json_string_of_devices_list"
                logdeviceset = set(json.loads(logdevices))
                if logdeviceset != deviceset:
                    # there has been a change in the devices
                    newstring = timestamp + " " + json.dumps(list(deviceset))
                    rconn.lpush(logkey, newstring)
                    # and limit number of logs
                    rconn.ltrim(logkey, 0, _LOGLENGTHS['devices'])
            # log changes in messages to logdata:messages
            messagelist = Message.get_message(rconn)
            if not messagelist:
                return
            logkey = key("logdata", "messages")
            logentry = rconn.lindex(logkey, 0)   # gets last log entry
            if logentry is None:
                newstring = timestamp + " " + json.dumps(messagelist)
                rconn.lpush(logkey, newstring)
            else:
                # Get the last log
                logtime, logmessage = logentry.decode("utf-8").split(" ", maxsplit=1)  # decode b"timestamp json_string_of_[timestamp message]"
                logmessagelist = json.loads(logmessage)
                if logmessagelist != messagelist:
                    # there has been a change in the message
                    newstring = timestamp + " " + json.dumps(messagelist)
                    rconn.lpush(logkey, newstring)
                    # and limit number of logs
                    rconn.ltrim(logkey, 0, _LOGLENGTHS['messages'])




######## Read a vector from redis ################


class _XMLVector():

    """Normally the vector used to create a property such as a TextVector
       is a received xml element object. However this class will be used to read redis and provide
       an object with the equivalent attrib dictionary attribute, and get method
       and will be iterable with child elements.
       It will be used to create the property vector object"""

    def __init__(self, rconn, device, name):
        "Provides a sequence object with attrib"
        # get the property attributes
        attribs = rconn.hgetall( key('attributes', name, device) )
        self.attrib = {key.decode("utf-8"):value.decode("utf-8") for key,value in attribs.items()}
        if not self.attrib:
            self.vector_type = None
            self.elements = []
            return
        self.vector_type = self.attrib['vector']
        # read the elements
        elements = rconn.smembers(key('elements', name, device))
        child_list = []
        for element_name in elements:
            ename = element_name.decode("utf-8")
            # for each element, read from redis and create a _XMLChild object, and set into child_list
            attributes = rconn.hgetall(key('elementattributes', ename, name, device))
            if self.vector_type == "BLOBVector":
                text = attributes.pop(b'value')      # Blobs are binary values, encoded with base64
                if text:
                    text = standard_b64encode(text)
            else:
                text = attributes.pop(b'value').decode("utf-8")
            child_list.append( _XMLChild(text, attributes) )
        self.elements = child_list

    def get(self, attribute, default=None):
        "This method obtains a specific attribute, equivalent to the xml element get method"
        return self.attrib.get(attribute, default)

    def __iter__(self):
        "Iterating over the vector gives the elements"
        for element in self.elements:
            yield element


class _XMLChild():
    """Set as elements within _XMLVector, each with attrib and text attributes and get method"""

    def __init__(self, text, attributes):
        "Provides an object with attrib and text attributes"
        self.attrib = {key.decode("utf-8"):value.decode("utf-8") for key,value in attributes.items()}
        self.text = text

    def get(self, attribute, default=None):
        "This method obtains a specific attribute, equivalent to the xml element get method"
        return self.attrib.get(attribute, default)



