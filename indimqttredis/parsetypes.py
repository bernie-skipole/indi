

from datetime import datetime

from collections.abc import MutableSequence


# From the INDI white paper:

# When a Client first starts up it knows nothing about the Devices and Properties it will control. It begins by connecting to a
# Device or indiserver and sending the getProperties command. This includes the protocol version and may include the name
# of a specific Device and Property if it is known by some other means. If no device is specified, then all devices are reported; if
# no name is specified, then all properties for the given device are reported.


# The Device then sends back one deftype element for each matching Property it offers for control,
# limited to the Properties of the specified Device if included. The deftype element shall always include
# all members of the vector for each Property.



# set the items for this module's api

__all__ = ['set_prefix', 'key', 'readvector', 'TextVector', 'NumberVector', 'SwitchVector', 'LightVector', 'BLOBVector', 'Message', 'delProperty' ] 



########## redis keys

_KEYPREFIX = ""


def set_prefix(key_prefix):
    "Sets the redis key prefix"
    global _KEYPREFIX
    if key_prefix:
        _KEYPREFIX = key_prefix
    else:
        _KEYPREFIX = ""


def key(*keys):
    "Add the prefix to keys, delimit keys with :"
    # example - if keys are 'device', 'property' this will result in a key of
    # 'keyprefix:device:property'
    return _KEYPREFIX + ":".join(keys)

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




############# Define properties



class ParentProperty():

    "Parent to Text, Number, Switch, Lights, Blob vectors"


    @classmethod
    def _read(cls, rconn, vector):
        "Create and return a class instance"
        device = vector.attrib['device']
        name = vector.attrib['name']
        # read the elements
        elements = rconn.smembers(key('elements', name, device))
        child_list = []
        for element_name in elements:
            ename = element_name.decode("utf-8")
            # for each element, read from redis and create a _Child object, and set into child_list
            attributes = rconn.hgetall(key('elementattributes', ename, name, device))
            text = attributes.pop(b'value')
            child_list.append( _Child(text, attributes) )
        vector.set_sequence(child_list)
        # this vector object can now be used to create a TextVector object
        return cls(vector)



    def __init__(self, vector):
        "Parent Item"
        attribs = vector.attrib
        # Required properties
        self.device = attribs.pop("device")    # name of Device
        self.name = attribs.pop("name")        # name of Property
        self.state = attribs.pop("state")      # current state of Property; Idle, OK, Busy or Alert

        # implied properties
        self.label = attribs.pop("label", self.name)                             # GUI label, use name by default
        self.group = attribs.pop("group", "")                                    # Property group membership, blank by default
        self.timestamp = attribs.pop("timestamp", datetime.utcnow().isoformat()) # moment when these data were valid
        self.message = attribs.pop("message", "")

        # add the class name so it is saved with attributes to redis, so the type of vector can be read
        self.vector = self.__class__.__name__


    def _set_permission(self, permission):
        "Sets the possible permissions, Read-Only, Write-Only or Read-Write"
        if permission in ('ro', 'wo', 'rw'):
            self.perm = permission
        else:
            self.perm = 'ro'


    def write(self, rconn):
        "Saves this device, and property to redis connection rconn"
        # add the device to redis set 'devices'
        rconn.sadd(key('devices'), self.device)                 # add device to 'devices'
        rconn.sadd(key('properties', self.device), self.name)   # add property name to 'properties:<devicename>'
        # Saves the instance attributes to redis, apart from self.element_list
        mapping = {key:value for key,value in self.__dict__.items() if key != "element_list"}
        rconn.hmset(key('attributes',self.name,self.device), mapping)
        # save list of element names
        for element in self.element_list:
            rconn.sadd(key('elements', self.name, self.device), element.name)   # add element name to 'elements:<propertyname>:<devicename>'



    def __str__(self):
        "Creates a string of label:states"
        if not self.element_list:
            return ""
        result = ""
        for element in self.element_list:
            result += element.label + " : " + str(element)+"\n"
        return result



class ParentElement():
    "Parent to Text, Number, Switch, Lights, Blob elements"

    def __init__(self, child):
        self.name = child.attrib["name"]                   # name of the element, required value
        self.label = child.attrib.get("label", self.name)  # GUI label, use name by default




################ Text ######################

class TextVector(ParentProperty):

    @classmethod
    def _read(cls, rconn, vector):
        "set vector.text, and vector elements"
        return super(TextVector, cls)._read(rconn, vector)



    def __init__(self, vector):
        "The vector is the xml defTextVector"
        attribs = vector.attrib
        perm = attribs.pop("perm")
        self._set_permission(perm)                 # ostensible Client controlability
        self.timeout = attribs.pop("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        self.element_list = []
        for child in vector:
            element = TextElement(child)
            self.element_list.append(element)
        super().__init__(vector)

    def write(self, rconn):
        "Saves name, label, value in 'elementattributes:<elementname>:<propertyname>:<devicename>'"
        for element in self.element_list:
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), element.__dict__)
        super().write(rconn)


class TextElement(ParentElement):
    "text elements contained in a TextVector"

    def __init__(self, child):
        value = child.text
        if value is None:
            self.value = ""
        else:
            self.value = value.strip()       # remove any newlines around the xml text
        super().__init__(child)

    def __str__(self):
        return self.value



################ Number ######################

class NumberVector(ParentProperty):

    @classmethod
    def _read(cls, rconn, vector):
        "set vector.text, and vector elements"
        return super(NumberVector, cls)._read(rconn, vector)

    def __init__(self, vector):
        "The vector is the defNumberVector"
        attribs = vector.attrib
        perm = attribs.pop("perm")
        self._set_permission(perm)                 # ostensible Client controlability
        self.timeout = attribs.pop("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        self.element_list = []
        for child in vector:
            element = NumberElement(child)
            self.element_list.append(element)
        super().__init__(vector)


    def write(self, rconn):
        "Saves name, label, format, min, max, step, value, formatted_number in 'elementattributes:<elementname>:<propertyname>:<devicename>'"
        for element in self.element_list:
            mapping = {key:value for key,value in element.__dict__.items()}
            mapping["formatted_number"] = element.formatted_number()
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), mapping)
        super().write(rconn)



class NumberElement(ParentElement):
    "number elements contained in a NumberVector"

    def __init__(self, child):
        # required number attributes
        self.format = child.attrib["format"]    # printf-style format for GUI display
        self.min = child.attrib["min"]       # minimal value
        self.max = child.attrib["max"]       # maximum value, ignore if min == max
        self.step = child.attrib["step"]      # allowed increments, ignore if 0
        # get the raw self.value
        self.value = child.text.strip()
        super().__init__(child)

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

    @classmethod
    def _read(cls, rconn, vector):
        "set vector.text, and vector elements"
        return super(SwitchVector, cls)._read(rconn, vector)


    def __init__(self, vector):
        "The vector is the xml defSwitchVector, containing child defSwich elements"
        attribs = vector.attrib
        perm = attribs.pop("perm")
        self._set_permission(perm)                 # ostensible Client controlability
        self.rule = attribs.pop("rule")            # hint for GUI presentation (OneOfMany|AtMostOne|AnyOfMany)
        self.timeout = attribs.pop("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        self.element_list = []
        for child in vector:
            element = SwitchElement(child)
            self.element_list.append(element)
        super().__init__(vector)

    def write(self, rconn):
        "Saves name, label, value in 'elementattributes:<elementname>:<propertyname>:<devicename>'"
        for element in self.element_list:
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), element.__dict__)
        super().write(rconn)


    def _set_permission(self, permission):
        "Sets the possible permissions, Read-Only or Read-Write"
        if permission in ('ro', 'rw'):
            self.perm = permission
        else:
            self.perm = 'ro'



class SwitchElement(ParentElement):
    "switch elements contained in a SwitchVector"

    def __init__(self, child):
        value = child.text
        # value should be Off or On"
        self.value = value.strip()       # remove any newlines around the xml text
        super().__init__(child)

    def __str__(self):
        return self.value



################ Lights ######################

class LightVector(ParentProperty):

    @classmethod
    def _read(cls, rconn, vector):
        "set vector.text, and vector elements"
        return super(LightVector, cls)._read(rconn, vector)

    def __init__(self, vector):
        "The vector is the defLightVector"
        self.perm = 'ro'                      # permission always Read-Only
        self.element_list = []
        for child in vector:
            element = LightElement(child)
            self.element_list.append(element)
        super().__init__(vector)

    def write(self, rconn):
        "Saves name, label, value in 'elementattributes:<elementname>:<propertyname>:<devicename>'"
        for element in self.element_list:
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), element.__dict__)
        super().write(rconn)


class LightElement(ParentElement):
    "light elements contained in a LightVector"

    def __init__(self, child):
        value = child.text
        # value should be (Idle|Ok|Busy|Alert)"
        self.value = value.strip()       # remove any newlines around the xml text
        super().__init__(child)

    def __str__(self):
        return self.value


        

################ BLOB ######################

class BLOBVector(ParentProperty):

    @classmethod
    def _read(cls, rconn, vector):
        "set vector.text, and vector elements"
        return super(BLOBVector, cls)._read(rconn, vector)

    def __init__(self, vector):
        "The vector is the defBLOBVector"
        attribs = vector.attrib
        perm = attribs.pop("perm")
        self._set_permission(perm)                 # ostensible Client controlability
        self.timeout = attribs.pop("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        self.element_list = []
        for child in vector:
            element = BLOBElement(child)
            self.element_list.append(element)
        super().__init__(vector)


    def write(self, rconn):
        "Saves name, label, value in 'elementattributes:<elementname>:<propertyname>:<devicename>'"
        for element in self.element_list:
            rconn.hmset(key('elementattributes',element.name, self.name, self.device), element.__dict__)
        super().write(rconn)


    def __str__(self):
        "Creates a string of labels"
        if not self.element_list:
            return ""
        result = ""
        for element in self.element_list:
            result += element.label + "\n"
        return result


class BLOBElement(ParentElement):
    "BLOB elements contained in a BLOBVector"


    def __init__(self, child):
        value = child.text
        if not value:
            self.value = ""
        super().__init__(child)


    def __str__(self):
        return ""



################ Message ####################


class Message():
    "a message associated with a device or entire system"

    def __init__(self, child):
        self.device = child.attrib.get("device", "")                                  # considered to be site-wide if absent
        self.timestamp = child.attrib.get("timestamp", datetime.utcnow().isoformat()) # moment when this message was generated
        self.message = child.attrib.get("message", "")                                # Received message


    def write(self, rconn):
        "Saves this message to a list, which contains the last ten messages"
        if not self.message:
            return
        time_and_message = self.timestamp + " " + self.message
        if self.device:
            rconn.lpush(key('devicemessages', self.device), time_and_message)
            # and limit number of messages to 10
            rconn.ltrim(key('devicemessages', self.device), 0, 9)
        else:
            rconn.lpush(key('messages'), time_and_message)
            # and limit number of messages to 10
            rconn.ltrim(key('messages'), 0, 9)

    def __str__(self):
        return self.message


################## Deleting #####################


class delProperty():

# A Device may tell a Client a given Property is no longer available by sending delProperty. If the command specifies only a
# Device without a Property, the Client must assume all the Properties for that Device, and indeed the Device itself, are no
# longer available.

    def __init__(self, child):
        "Delete the given property, or device if property name is None"
        self.device = child.attrib.get("device")
        self.name = child.attrib.get("name", "")
        self.timestamp = child.attrib.get("timestamp", datetime.utcnow().isoformat()) # moment when this message was generated
        self.message = child.attrib.get("message", "")                                # Received message


    def write(self, rconn):
        "Deletes the property or device from redis"
        if self.name:
            # delete the property and add the message to the device message list
            if self.message:
                time_and_message = f"{self.timestamp} {self.message}"
            else:
                time_and_message = f"{self.timestamp} Property {self.name} deleted from device {self.device}"
            rconn.lpush(key('messages', self.device), time_and_message)
            # and limit number of messages to 10
            rconn.ltrim(key('messages', self.device), 0, 9)
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
            # delete the device and add the message to the system message list
            if self.message:
                time_and_message = f"{self.timestamp} {self.message}"
            else:
                time_and_message = f"{self.timestamp} {self.device} deleted"
            rconn.lpush(key('messages'), time_and_message)
            # and limit number of messages to 10
            rconn.ltrim(key('messages'), 0, 9)
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


######## Read a vector from redis ################


class _Vector():

    """Normally the vector used to create a property such as a TextVector
       is an xml element object. However this class will be used to provide
       an object with the equivalent attrib dictionary attribute, and will be iterable
       with child elements.
       It will be filled by the property _read classmethod, and then used to create
       the property vector object"""

    def __init__(self, attributes):
        "Provides a sequence object with attrib"
        self.attrib = {key.decode("utf-8"):value.decode("utf-8") for key,value in attributes.items()}
        self.elements = []

    def set_sequence(self, elements):
        "Set a list of elements into this vector"
        self.elements = elements

    def __iter__(self):
        self.e_iterator = iter(self.elements)
        return self

    def __next__(self):
        return next(self.e_iterator)




class _Child():

    def __init__(self, text, attributes):
        "Provides an object with attrib and text attributes"
        self.attrib = {key.decode("utf-8"):value.decode("utf-8") for key,value in attributes.items()}
        self.text = text.decode("utf-8")


def readvector(rconn, device, name):
    """Where device is the device name, name is the vector name,
       reads redis and returns an instance of a *Vector class"""
    # If device is not in the 'devices' set, return None
    if not rconn.sismember(key('devices'), device):
        return
    # If the vector is not recognised as a property of the device, return None
    if not rconn.sismember(key('properties', device), name):
        return
    # get the property attributes
    attributes = rconn.hgetall( key('attributes', name, device) )
    if not attributes:
        return None
    # keys and values of all attributes are binary
    # create an object with attrib and a sequence
    vector = _Vector(attributes)
    # The vector attribute gives the class
    vector_type = attributes[b'vector']
    if vector_type == b"TextVector":
        return TextVector._read(rconn, vector)
    elif vector_type == b"NumberVector":
        return NumberVector._read(rconn, vector)
    elif vector_type == b"SwitchVector":
        return SwitchVector._read(rconn, vector)
    elif vector_type == b"LightVector":
        return LightVector._read(rconn, vector)
    elif vector_type == b"BLOBVector":
        return BLOBVector._read(rconn, vector)


