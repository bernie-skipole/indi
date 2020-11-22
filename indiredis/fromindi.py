

###################
#
#  fromindi.py
#
###################


"""Reads indi xml strings, parses them and places values into redis,
ready for reading by the web server."""


import xml.etree.ElementTree as ET

import os, math, json, pathlib

from datetime import datetime

from base64 import standard_b64decode, standard_b64encode

from . import tools


# All xml data received should be contained in one of the following tags
TAGS = (b'defTextVector',
        b'defNumberVector',
        b'defSwitchVector',
        b'defLightVector',
        b'defBLOBVector',
        b'message',
        b'delProperty',
        b'setTextVector',
        b'setNumberVector',
        b'setSwitchVector',
        b'setLightVector',
        b'setBLOBVector'
       )




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

_BLOBFOLDER = ""



def receive_from_indiserver(data, root, rconn):
    """receives xml data, parses it and stores in redis. Publishes the data received on _FROM_INDI_CHANNEL,
       returns device name if given, or None"""
    global _FROM_INDI_CHANNEL
    if rconn is None:
        return
    # this timestamp is the time at which the data is received
    timestamp = datetime.utcnow().isoformat(sep='T')

    devicename = None

    if root.tag == "defTextVector":
        text_vector = TextVector()                      # create a TextVector object
        text_vector.setup_from_def(rconn, root)         # store the received data in a TextVector object
        text_vector.write(rconn)                        # call the write method to store data in redis
        text_vector.log(rconn, timestamp)
        devicename = text_vector.device
    elif root.tag == "defNumberVector":
        number_vector = NumberVector()
        number_vector.setup_from_def(rconn, root)
        number_vector.write(rconn)
        number_vector.log(rconn, timestamp)
        devicename = number_vector.device
    elif root.tag == "defSwitchVector":
        switch_vector = SwitchVector()
        switch_vector.setup_from_def(rconn, root)
        switch_vector.write(rconn)
        switch_vector.log(rconn, timestamp)
        devicename = switch_vector.device
    elif root.tag == "defLightVector":
        light_vector = LightVector()
        light_vector.setup_from_def(rconn, root)
        light_vector.write(rconn)
        light_vector.log(rconn, timestamp)
        devicename = light_vector.device
    elif root.tag == "defBLOBVector":
        blob_vector = BLOBVector()
        blob_vector.setup_from_def(rconn, root)
        blob_vector.write(rconn)
        blob_vector.log(rconn, timestamp)
        devicename = blob_vector.device
    elif root.tag == "message":
        message = Message(root)
        message.write(rconn)
        message.log(rconn, timestamp)
    elif root.tag == "delProperty":
        delprop = delProperty(root)
        delprop.write(rconn)
        delprop.log(rconn, timestamp)
    elif root.tag == "setTextVector":
        text_vector = TextVector.update_from_setvector(rconn, root)
        if text_vector is not None:
            text_vector.log(rconn, timestamp)
    elif root.tag == "setNumberVector":
        number_vector = NumberVector.update_from_setvector(rconn, root)
        if number_vector is not None:
            number_vector.log(rconn, timestamp)
    elif root.tag == "setSwitchVector":
        switch_vector = SwitchVector.update_from_setvector(rconn, root)
        if switch_vector is not None:
            switch_vector.log(rconn, timestamp)
    elif root.tag == "setLightVector":
        light_vector = LightVector.update_from_setvector(rconn, root)
        if light_vector is not None:
            light_vector.log(rconn, timestamp)
    elif root.tag == "setBLOBVector":
        blob_vector = BLOBVector.update_from_setvector(rconn, root)
        if blob_vector is not None:
            blob_vector.log(rconn, timestamp)
    # and publishes the data received
    rconn.publish(_FROM_INDI_CHANNEL, data)
    return devicename


def setup_redis(key_prefix, to_indi_channel, from_indi_channel, log_lengths, blob_folder):
    "Sets the redis key prefix and pubsub channels"
    global _KEYPREFIX, _TO_INDI_CHANNEL, _FROM_INDI_CHANNEL, _LOGLENGTHS, _BLOBFOLDER

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
    if log_lengths:
        # ensure no item in log_lengths has a value less than 1
        new_log_lengths = {}
        for key,value in log_lengths.items():
            if value<1:
                new_log_lengths[key]=1
            else:
                new_log_lengths[key]=value
        _LOGLENGTHS.update(new_log_lengths)
    if blob_folder:
        _BLOBFOLDER = blob_folder
    else:
        _BLOBFOLDER = ""


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

    def __init__(self):
        "Parent Item"
        # add the class name so it is saved with attributes to redis, so the type of vector can be read
        self.vector = self.__class__.__name__
        # self.elements is a dictionary which will hold the elements within this vector, keys are element names
        self.elements = {}


    def setup_from_def(self, rconn, vector):
        "Set up the object from def... element"
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
        self.label = vector.get("label", self.name)                             # GUI label, use name by default
        self.group = vector.get("group", "DEFAULT GROUP")                       # Property group membership, blank by default
        self.timestamp = vector.get("timestamp", datetime.utcnow().isoformat()) # moment when these data were valid
        self.message = vector.get("message", "")


    def setup_from_redis(self, rconn, device, name):
        "Set up the object from set... element"
        self.device = device    # name of Device
        self.name = name        # name of Property
        self._status = False     # read status, will be set to True if items read from redis are ok
        # read attributes from redis
        self._strattribs = self.get_attributes(rconn)
        # this should be a dictionary of attributes, if not found, it will be an empty dictionary
        if not self._strattribs:
            # returns with an empty self._strattribs
            return
        self.state = self._strattribs["state"]
        self.label = self._strattribs["label"]
        self.group = self._strattribs["group"]
        self.timestamp = self._strattribs["timestamp"]
        self.message = self._strattribs["message"]

    def _set_permission(self, permission):
        "Sets the possible permissions, Read-Only, Write-Only or Read-Write"
        if permission in ('ro', 'wo', 'rw'):
            self.perm = permission
        else:
            self.perm = 'ro'

    @staticmethod
    def get_devices(rconn):
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
        mapping = {key:value for key,value in self.__dict__.items() if (key != "elements") and (not key.startswith("_"))}
        rconn.hmset(key('attributes',self.name,self.device), mapping)
        # save updated elements
        for element in self.elements.values():
            element.write(rconn, self.device, self.name)
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
        # create an object of this class
        obj = cls()
        obj.setup_from_redis(rconn, device, name)
        if not obj._status:
            return
        return obj


    def update(self, rconn, vector):
        "Update the object attributes to redis"
        self.timestamp = vector.get("timestamp", datetime.utcnow().isoformat()) # moment when these data were valid
        # timestamp updated before elements updated, in case any of the elements use the timestamp (BLOBs)
        for child in vector:
            element = self.elements[child.get("name")]
            element.update(rconn, self.device, self.name, child, timestamp=self.timestamp)
        # alter self according to the values to be set
        state = vector.get("state")     # set state of Property; Idle, OK, Busy or Alert, no change if absent
        if state:
            self.state = state
        self.message = vector.get("message", "")
        # Saves the instance attributes to redis, apart from self.elements
        mapping = {key:value for key,value in self.__dict__.items() if (key != "elements") and (not key.startswith("_"))}
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

    def setup_from_def(self, child, **kwargs):
        self.name = child.get("name")                       # name of the element, required value
        self.label = child.get("label", self.name)  # GUI label, use name by default


    def setup_from_redis(self, rconn, device, name, element_name):
        self.name = element_name.decode("utf-8")
        self._status = False     # read status, will be set to True if items read from redis are ok
        self._strattribs = self.get_attributes(rconn, device, name)
        if not self._strattribs:
            return
        self.label = self._strattribs["label"]


    def get_attributes(self, rconn, device, name):
        "Returns a dictionary of attributes for this element, given property name and device as saved in redis"
        attdict = rconn.hgetall(key('elementattributes', self.name, name, device))
        if not attdict:
            return {}
        return {k.decode("utf-8"):v.decode("utf-8") for k,v in attdict.items()}


    def write(self, rconn, device, name):
        "Writes element attributes to redis"
        # create dictionary of non-private attributes
        attribs = {key:val for key,val in self.__dict__.items() if not key.startswith("_")}
        if attribs:
            rconn.hmset(key('elementattributes',self.name, name, device), attribs)

    def update(self, rconn, device, name, child, **kwargs):
        "update the element, from a vector child, and write to redis"
        self.set_value(child)   # change value to that given by the xml child
        self.write(rconn, device, name)

    def set_value(self, child):
        if (child is None) or (not child.text):
            self.value = ""
        else:
            self.value = child.text.strip()       # remove any newlines around the xml text



################ Text ######################

class TextVector(ParentProperty):


    def setup_from_def(self, rconn, vector):
        "Set up the object from def... element"
        super().setup_from_def(rconn, vector)
        perm = vector.get("perm")
        self._set_permission(perm)                 # ostensible Client controlability
        self.timeout = vector.get("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        for child in vector:
            element = TextElement()
            element.setup_from_def(child)
            self.elements[element.name] = element

    def setup_from_redis(self, rconn, device, name):
        "Set up the object from set... element"
        super().setup_from_redis(rconn, device, name)
        if not self._strattribs:
            # failed to read attributes
            return
        # the super call has set self._strattribs
        self.perm = self._strattribs["perm"]
        self.timeout = self._strattribs["timeout"]
        # read the elements
        elements = rconn.smembers(key('elements', name, device))
        if not elements:
            return
        for element_name in elements:
            element = TextElement()
            element.setup_from_redis(rconn, device, name, element_name)
            if not element._status:
                # failure to read the element
                return
            self.elements[element.name] = element
        self._status = True     # read status set to True, redis read successful

    def update(self, rconn, vector):
        "Update the object attributes and changed elements to redis"
        self.timeout = vector.get("timeout", 0)
        super().update(rconn, vector)


class TextElement(ParentElement):
    "text elements contained in a TextVector"

    def setup_from_def(self, child, **kwargs):
        self.set_value(child)
        super().setup_from_def(child, **kwargs)

    def setup_from_redis(self, rconn, device, name, element_name):
        "Sets up element by reading redis"
        super().setup_from_redis(rconn, device, name, element_name)
        if not self._strattribs:
            # failed to read attributes
            return
        self.value = self._strattribs["value"]
        self._status = True

    def __str__(self):
        return self.value



################ Number ######################

class NumberVector(ParentProperty):


    def setup_from_def(self, rconn, vector):
        "Set up the object from def... element"
        super().setup_from_def(rconn, vector)
        perm = vector.get("perm")
        self._set_permission(perm)                 # ostensible Client controlability
        self.timeout = vector.get("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        for child in vector:
            element = NumberElement()
            element.setup_from_def(child)
            self.elements[element.name] = element

    def setup_from_redis(self, rconn, device, name):
        "Set up the object from set... element"
        super().setup_from_redis(rconn, device, name)
        if not self._strattribs:
            # failed to read attributes
            return
        # the super call has set self._strattribs
        self.perm = self._strattribs["perm"]
        self.timeout = self._strattribs["timeout"]
        # read the elements
        elements = rconn.smembers(key('elements', name, device))
        if not elements:
            return
        for element_name in elements:
            element = NumberElement()
            element.setup_from_redis(rconn, device, name, element_name)
            if not element._status:
                # failure to read the element
                return
            self.elements[element.name] = element
        self._status = True     # read status set to True, redis read successful


    def update(self, rconn, vector):
        "Update the object attributes and changed elements to redis"
        self.timeout = vector.get("timeout", 0)
        super().update(rconn, vector)



class NumberElement(ParentElement):
    "number elements contained in a NumberVector"

    def setup_from_def(self, child, **kwargs):
        # required number attributes
        self.format = child.get("format")    # printf-style format for GUI display
        self.min = child.get("min")          # minimal value
        self.max = child.get("max")           # maximum value, ignore if min == max
        self.step = child.get("step")        # allowed increments, ignore if 0
        # get the raw self.value
        self.set_value(child)
        super().setup_from_def(child, **kwargs)

    def setup_from_redis(self, rconn, device, name, element_name):
        "Sets up element by reading redis"
        super().setup_from_redis(rconn, device, name, element_name)
        if not self._strattribs:
            # failed to read attributes
            return
        self.format = self._strattribs["format"]
        self.min = self._strattribs["min"]
        self.max = self._strattribs["max"]
        self.step = self._strattribs["step"]
        self.value = self._strattribs["value"]
        self._status = True


    def write(self, rconn, device, name):
        "Writes element attributes to redis"
        # create dictionary of non-private attributes
        attribs = {key:val for key,val in self.__dict__.items() if not key.startswith("_")}
        attribs["formatted_number"] = self.formatted_number()
        attribs["float_number"] = self.float_number()
        attribs["float_min"] = self.float_min()
        attribs["float_max"] = self.float_max()
        attribs["float_step"] = self.float_step()
        rconn.hmset(key('elementattributes',self.name, name, device), attribs)


    def formatted_number(self):
        """Returns the string of the number using the format value"""
        floatvalue = self.float_number()
        return tools.format_number(floatvalue, self.format)

    def float_number(self):
        """Returns the float of the number value"""
        return tools.number_to_float(self.value)

    def float_min(self):
        "Returns the float of the min value"
        return tools.number_to_float(self.min)

    def float_max(self):
        "Returns the float of the max value"
        return tools.number_to_float(self.max)

    def float_step(self):
        "Returns the float of the step value"
        return tools.number_to_float(self.step)

    def __str__(self):
        "Returns the formatted number, equivalent to self.formatted_number()"
        return self.formatted_number()


################ Switch ######################

class SwitchVector(ParentProperty):

    def setup_from_def(self, rconn, vector):
        "Set up the object from def... element"
        super().setup_from_def(rconn, vector)
        perm = vector.get("perm")
        self._set_permission(perm)                          # ostensible Client controlability
        self.rule = vector.get("rule")                      # hint for GUI presentation (OneOfMany|AtMostOne|AnyOfMany)
        self.timeout = vector.get("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro

        for child in vector:
            element = SwitchElement()
            element.setup_from_def(child)
            self.elements[element.name] = element

    def setup_from_redis(self, rconn, device, name):
        "Set up the object from set... element"
        super().setup_from_redis(rconn, device, name)
        if not self._strattribs:
            # failed to read attributes
            return
        # the super call has set self._strattribs
        self.perm = self._strattribs["perm"]
        self.rule = self._strattribs["rule"]
        self.timeout = self._strattribs["timeout"]
        # read the elements
        elements = rconn.smembers(key('elements', name, device))
        if not elements:
            return
        for element_name in elements:
            element = SwitchElement()
            element.setup_from_redis(rconn, device, name, element_name)
            if not element._status:
                # failure to read the element
                return
            self.elements[element.name] = element
        self._status = True     # read status set to True, redis read successful

    def update(self, rconn, vector):
        "Update the object attributes and changed elements to redis"
        self.timeout = vector.get("timeout", 0)
        super().update(rconn, vector)

    def _set_permission(self, permission):
        "Sets the possible permissions, Read-Only or Read-Write"
        if permission in ('ro', 'rw'):
            self.perm = permission
        else:
            self.perm = 'ro'



class SwitchElement(ParentElement):
    "switch elements contained in a SwitchVector"

    def setup_from_def(self, child, **kwargs):
        "value should be Off or On"
        self.set_value(child)
        super().setup_from_def(child, **kwargs)


    def setup_from_redis(self, rconn, device, name, element_name):
        "Sets up element by reading redis"
        super().setup_from_redis(rconn, device, name, element_name)
        if not self._strattribs:
            # failed to read attributes
            return
        self.value = self._strattribs["value"]
        self._status = True


    def __str__(self):
        return self.value



################ Lights ######################

class LightVector(ParentProperty):


    def setup_from_def(self, rconn, vector):
        "Set up the object from def... element"
        super().setup_from_def(rconn, vector)
        self.perm = 'ro'                      # permission always Read-Only
        for child in vector:
            element = LightElement()
            element.setup_from_def(child)
            self.elements[element.name] = element

    def setup_from_redis(self, rconn, device, name):
        "Set up the object from set... element"
        super().setup_from_redis(rconn, device, name)
        if not self._strattribs:
            # failed to read attributes
            return
        # the super call has set self._strattribs
        self.perm = 'ro'
        # read the elements
        elements = rconn.smembers(key('elements', name, device))
        if not elements:
            return
        for element_name in elements:
            element = LightElement()
            element.setup_from_redis(rconn, device, name, element_name)
            if not element._status:
                # failure to read the element
                return
            self.elements[element.name] = element
        self._status = True     # read status set to True, redis read successful



class LightElement(ParentElement):
    "light elements contained in a LightVector"

    def setup_from_def(self, child, **kwargs):
        self.set_value(child)
        super().setup_from_def(child, **kwargs)


    def setup_from_redis(self, rconn, device, name, element_name):
        "Sets up element by reading redis"
        super().setup_from_redis(rconn, device, name, element_name)
        if not self._strattribs:
            # failed to read attributes
            return
        self.value = self._strattribs["value"]
        self._status = True

    def __str__(self):
        return self.value


        

################ BLOB ######################

class BLOBVector(ParentProperty):

    def setup_from_def(self, rconn, vector):
        "Set up the object from def... element"
        super().setup_from_def(rconn, vector)
        perm = vector.get("perm")
        self._set_permission(perm)                          # ostensible Client controlability
        self.timeout = vector.get("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        # as default blobs are disabled, check if this device is already known
        # in redis and if blobs were previously enabled
        attribs = self.get_attributes(rconn)
        if attribs and attribs['blobs'] == "Enabled":
            self.blobs = "Enabled"
        else:
            self.blobs = "Disabled"
        for child in vector:
            element = BLOBElement(self.timestamp)
            element.setup_from_def(child, timestamp=self.timestamp)
            # A defBLOB only has name and label, contents are empty, however if blobs are enabled
            # and this BLOB element has been previously defined, and a filepath saved in redis,
            # then get element pathname etc from redis
            if self.blobs == "Enabled":
                element.set_file(rconn, self.device, self.name, child)
            self.elements[element.name] = element

    def setup_from_redis(self, rconn, device, name):
        "Set up the object from set... element"
        super().setup_from_redis(rconn, device, name)
        if not self._strattribs:
            # failed to read attributes
            return
        # the super call has set self._strattribs
        self.perm = self._strattribs["perm"]
        self.timeout = self._strattribs["timeout"]
        self.blobs = self._strattribs["blobs"]
        # read the elements
        elements = rconn.smembers(key('elements', name, device))
        if not elements:
            return
        for element_name in elements:
            element = BLOBElement(self.timestamp)
            element.setup_from_redis(rconn, device, name, element_name)
            if not element._status:
                # failure to read the element
                return
            self.elements[element.name] = element
        self._status = True     # read status set to True, redis read successful


    def update(self, rconn, vector):
        "Update the object attributes and changed elements to redis"
        # as this is only called when a setBLOBVector is received, it must mean that blobs are enabled
        self.blobs = "Enabled"
        super().update(rconn, vector)


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


    def __init__(self, timestamp):
        "Adds timestamp to self, used for filenames"
        super().__init__()
        self.timestamp = timestamp

    def setup_from_def(self, child, **kwargs):
        "Set up element from xml"
        # A defBLOB only has name and label, contents are empty
        # name and label are set in super
        super().setup_from_def(child, **kwargs)
        # initialise data
        self.size =  ""     # number of bytes in decoded and uncompressed BLOB
        self.format = ""    # format as a file suffix, eg: .z, .fits, .fits.z
        self.filepath = ""
        if 'timestamp' in kwargs:
            self.timestamp = kwargs["timestamp"]


    def setup_from_redis(self, rconn, device, name, element_name):
        "Sets up element by reading redis"
        super().setup_from_redis(rconn, device, name, element_name)
        if not self._strattribs:
            # failed to read attributes
            return
        self.size = self._strattribs["size"]
        self.format = self._strattribs["format"]
        self.filepath = self._strattribs["filepath"]
        self.timestamp = self._strattribs["timestamp"]
        self._status = True

    def update(self, rconn, device, name, child, **kwargs):
        "update the element, from a vector child, and write to redis"
        self.size = child.get("size")     # number of bytes in decoded and uncompressed BLOB
        self.format = child.get("format") # format as a file suffix, eg: .z, .fits, .fits.z
        if 'timestamp' in kwargs:
            self.timestamp = kwargs['timestamp']
        # If child.text, save standard_b64decode(child.text) to a file
        # and set the new filepath attribute of the element
        self.set_file(rconn, device, name, child)
        self.write(rconn, device, name)

    def set_value(self, child):
        "value is not used for a Blob"
        return


    def set_file(self, rconn, devicename, propertyname, child):
        """If child.text is blob data, this saves the file, and sets a filepath attribute
           If no text, checks if redis contains a previous filepath and uses that"""
        if not _BLOBFOLDER:
            return
        # check if the _BLOBFOLDER exists
        if not _BLOBFOLDER.exists():
            # if not, create it
            _BLOBFOLDER.mkdir(parents=True)
        if child.text is None:
            # no new file
            # Check if a filepath exists in redis
            attribs = self.get_attributes(rconn, devicename, propertyname)
            if not attribs:
                # no new file is given in child.text, nor any file currently exists
                return
            # read from attributes, may not exist, so use the empty defaults
            self.filepath = attribs.get("filepath", "")
            if self.filepath:
                self.size = attribs.get("size","")
                self.format = attribs.get("format","")
                self.timestamp = attribs.get("timestamp", self.timestamp)
            return
        # a new file exists in child.text
        # make filename from timestamp, and change colon in the timestamp to _ for safer name
        filename =  self.timestamp.replace(":", "_") + self.format
        counter = 0
        while True:
            filepath = _BLOBFOLDER / filename
            if filepath.exists():
                # append a digit to the filename
                counter += 1
                filename = self.timestamp.replace(":", "_") + "_" + str(counter) + self.format
            else:
                # filepath does not exist, so a new file with this filepath can be created
                break
        filepath.write_bytes(standard_b64decode(child.text))
        self.filepath = str(filepath)
        # size and format are specified in the child vector

    def __str__(self):
        return ""



################ Message ####################


class Message():
    "a message associated with a device or entire system"

    def __init__(self, child):
        self.device = child.get("device", "")                                  # considered to be site-wide if absent
        self.timestamp = child.get("timestamp", datetime.utcnow().isoformat()) # moment when this message was generated
        self.message = child.get("message", "")                                # Received message


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
        self.name = child.get("name", "")
        self.timestamp = child.get("timestamp", datetime.utcnow().isoformat()) # moment when this message was generated
        self.message = child.get("message", "")                                # Received message


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


