

from datetime import datetime

import redis


# From the INDI white paper:

# When a Client first starts up it knows nothing about the Devices and Properties it will control. It begins by connecting to a
# Device or indiserver and sending the getProperties command. This includes the protocol version and may include the name
# of a specific Device and Property if it is known by some other means. If no device is specified, then all devices are reported; if
# no name is specified, then all properties for the given device are reported.


# The Device then sends back one deftype element for each matching Property it offers for control,
# limited to the Properties of the specified Device if included. The deftype element shall always include
# all members of the vector for each Property.


############## redis connection

# redisserver is a named tuple with attributes: 'host', 'port', 'db', 'password', 'keyprefix'

_REDISCONNECTION = None

_KEYPREFIX = ''


def open_redis(redisserver):
    "Returns a connection to the redis database, on failure returns None"
    global _KEYPREFIX, _REDISCONNECTION
    _KEYPREFIX = redisserver.keyprefix
    if _KEYPREFIX:
        _KEYPREFIX += ":"
    try:
        if _REDISCONNECTION is None:
            # create a connection to redis
            _REDISCONNECTION = redis.StrictRedis(host=redisserver.host,
                                                 port=redisserver.port,
                                                 db=redisserver.db,
                                                 password=redisserver.password,
                                                 socket_timeout=5)
    except Exception:
        _REDISCONNECTION = None
    return _REDISCONNECTION


########## redis keys

def key(*keys):
    "Add the prefix to keys, delimit keys with :"
    # example - if keys are 'device', 'property' this will result in a key of
    # 'keyprefix:device:property'
    return _KEYPREFIX + ":".join(keys)
    


############# Define properties


class ParseProperty():

    "Parent to Text, Number, Switch, Lights, Blob vectors"

    def __init__(self, vector):
        "Parent Item"
        attribs = vector.attrib
        # Required properties
        self.device = attribs.pop("device")    # name of Device
        # add this device to redis set 'devices'
        _REDISCONNECTION.sadd(key('devices'), self.device)
        self.name = attribs.pop("name")        # name of Property
        self.state = attribs.pop("state")      # current state of Property; Idle, OK, Busy or Alert

        # implied properties
        self.label = attribs.pop("label", self.name)                             # GUI label, use name by default
        self.group = attribs.pop("group", "")                                    # Property group membership, blank by default
        self.timestamp = attribs.pop("timestamp", datetime.utcnow().isoformat()) # moment when these data were valid
        self.message = attribs.pop("message", "")


    def _set_permission(self, permission):
        "Sets the possible permissions, Read-Only, Write-Only or Read-Write"
        if permission in ('ro', 'wo', 'rw'):
            self.permission = permission
        else:
            self.permission = 'ro'       


    # To inform a Client of new current values for a Property and their state, a Device sends one settype element. It is only
    # required to send those members of the vector that have changed.

    def settype(self, values):
        "elements:values that have changed"
        pass


    def __str__(self):
        "Creates a string of label:states"
        if not self.element_list:
            return ""
        result = ""
        for element in self.element_list:
            result += element.label + " : " + str(element)+"\n"
        return result



class ParseElement():
    "Parent to Text, Number, Switch, Lights, Blob elements"

    def __init__(self, child):
        self.name = child.attrib["name"]                   # name of the element, required value
        self.label = child.attrib.get("label", self.name)  # GUI label, use name by default




################ Text ######################

class ParseTextVector(ParseProperty):

    def __init__(self, vector):
        "The vector is the xml defTextVector"
        attribs = vector.attrib
        perm = attribs.pop("perm")
        self._set_permission(perm)                 # ostensible Client controlability
        self.timeout = attribs.pop("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        self.element_list = []
        for child in vector:
            element = ParseText(child)
            self.element_list.append(element)
        super().__init__(vector)


class ParseText(ParseElement):
    "text elements contained in a ParseTextVector"

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

class ParseNumberVector(ParseProperty):

    def __init__(self, vector):
        "The vector is the defNumberVector"
        attribs = vector.attrib
        perm = attribs.pop("perm")
        self._set_permission(perm)                 # ostensible Client controlability
        self.timeout = attribs.pop("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        self.element_list = []
        for child in vector:
            element = ParseNumber(child)
            self.element_list.append(element)
        super().__init__(vector)



class ParseNumber(ParseElement):
    "number elements contained in a defNumberVector"

    def __init__(self, child):
        # required number attributes
        self.format = child.attrib["format"]    # printf-style format for GUI display
        self.min = child.attrib["min"]       # minimal value
        self.max = child.attrib["max"]       # maximum value, ignore if min == max
        self.step = child.attrib["step"]      # allowed increments, ignore if 0
        # get the raw self.value
        self.value = child.text.strip()
        super().__init__(child)

    def __str__(self):
        """Returns the string of the number using the format value"""
        # Splits the number into a negative flag and three sexagesimal parts
        # then calls self._sexagesimal or self._printf to create the formatted string"""
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


################ Switch ######################

class ParseSwitchVector(ParseProperty):


    def __init__(self, vector):
        "The vector is the xml defSwitchVector, containing child defSwich elements"
        attribs = vector.attrib
        perm = attribs.pop("perm")
        self._set_permission(perm)                 # ostensible Client controlability
        self.rule = attribs.pop("rule")            # hint for GUI presentation (OneOfMany|AtMostOne|AnyOfMany)
        self.timeout = attribs.pop("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        self.element_list = []
        for child in vector:
            element = ParseSwitch(child)
            self.element_list.append(element)
        super().__init__(vector)


    def _set_permission(self, permission):
        "Sets the possible permissions, Read-Only or Read-Write"
        if permission in ('ro', 'rw'):
            self.permission = permission
        else:
            self.permission = 'ro'



class ParseSwitch(ParseElement):
    "switch elements contained in a ParseSwitchVector"

    def __init__(self, child):
        value = child.text
        # value should be Off or On"
        self.value = value.strip()       # remove any newlines around the xml text
        super().__init__(child)

    def __str__(self):
        return self.value



################ Lights ######################

class ParseLightVector(ParseProperty):

    def __init__(self, vector):
        "The vector is the defLightVector"
        self.permission = 'ro'                      # permission always Read-Only
        self.element_list = []
        for child in vector:
            element = ParseLight(child)
            self.element_list.append(element)
        super().__init__(vector)


class ParseLight(ParseElement):
    "light elements contained in a ParseLightVector"

    def __init__(self, child):
        value = child.text
        # value should be (Idle|Ok|Busy|Alert)"
        self.value = value.strip()       # remove any newlines around the xml text
        super().__init__(child)

    def __str__(self):
        return self.value


        

################ BLOB ######################

class ParseBLOBVector(ParseProperty):

    def __init__(self, vector):
        "The vector is the defBLOBVector"
        attribs = vector.attrib
        perm = attribs.pop("perm")
        self._set_permission(perm)      # ostensible Client controlability
        self.timeout = attribs.pop("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        self.element_list = []
        for child in vector:
            element = ParseBLOB(child)
            self.element_list.append(element)
        super().__init__(vector)


    def __str__(self):
        "Creates a string of labels"
        if not self.element_list:
            return ""
        result = ""
        for element in self.element_list:
            result += element.label + "\n"
        return result


class ParseBLOB(ParseElement):
    "BLOB elements contained in a ParseBLOBVector"

    # Unlike other defXXX elements, this does not contain an
    # initial value for the BLOB.

    def __str__(self):
        return ""



################ Message ####################


class ParseMessage():
    "a message associated with a device or entire system"

    def __init__(self, child):
        self.device = child.attrib.get["device", ""]                                  # considered to be site-wide if absent
        self.timestamp = child.attrib.get("timestamp", datetime.utcnow().isoformat()) # moment when this message was generated
        self.message = child.attrib.get("message", "")                                # Received message

    def __str__(self):
        return self.message


################## Deleting #####################


class delProperty():

# A Device may tell a Client a given Property is no longer available by sending delProperty. If the command specifies only a
# Device without a Property, the Client must assume all the Properties for that Device, and indeed the Device itself, are no
# longer available.

    def __init__(self, device, dproperty, **kwds):    # dproperty is used instead of property to avoid confusion with the Python 'property'
        "Delete the given property, or all if dproperty is None"
        self.device = device
        self.dproperty = dproperty
        super().__init__(**kwds)




############ Function which receives the xml tree ###############

def receive_tree(root):
    "Receives the element tree root"
    for child in root:
        if child.tag == "defTextVector":
            text_vector = ParseTextVector(child)
            print(text_vector.device, text_vector.name)
            print(str(text_vector))
        if child.tag == "defNumberVector":
            number_vector = ParseNumberVector(child)
            print(number_vector.device, number_vector.name)
            print(str(number_vector))
        if child.tag == "defSwitchVector":
            switch_vector = ParseSwitchVector(child)
            print(switch_vector.device, switch_vector.name)
            print(str(switch_vector))
        if child.tag == "defLightVector":
            light_vector = ParseLightVector(child)
            print(light_vector.device, light_vector.name)
            print(str(light_vector))
        if child.tag == "defBLOBVector":
            blob_vector = ParseBLOBVector(child)
            print(blob_vector.device, blob_vector.name)
            print(str(blob_vector))
        if child.tag == "message":
            message = ParseMessage(child)
            print(message.device, str(message))
    # devices are those received in this exchange, list of binary names
    devices = _REDISCONNECTION.smembers(key('devices'))
    if devices:
        device_names = list(dn.decode("utf-8") for dn in devices)
        device_names.sort()
        print(device_names)









