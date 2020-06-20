

from datetime import datetime


# When a Client first starts up it knows nothing about the Devices and Properties it will control. It begins by connecting to a
# Device or indiserver and sending the getProperties command. This includes the protocol version and may include the name
# of a specific Device and Property if it is known by some other means. If no device is specified, then all devices are reported; if
# no name is specified, then all properties for the given device are reported.


# The Device then sends back one deftype element
# for each matching Property it offers for control, limited to the Properties of the specified Device if included. The deftype
# element shall always include all members of the vector for each Property.


class Group():

    "Properties may be assembled into groups"

    def __init__(self, members, **kwds):
        self.members = members
        super().__init__(**kwds)


class Device(Group):

    """Each command between Client and Device specifies a Device name and Property name.
       The Device name serves as a logical grouping of several Properties"""

    def __init__(self, name, **kwds):
        self.name = name
        super().__init__(**kwds)


class ParseMessage():

# A Device may send out a message either as part of another command or by itself. When sent alone a message may be
# associated with a specific Device or just to the Client in general.

    def __init__(self, message, timestamp=None, device=None, **kwds):
        self.message = message
        self.timestamp = timestamp
        self.device = device
        super().__init__(**kwds)


class delProperty():

# A Device may tell a Client a given Property is no longer available by sending delProperty. If the command specifies only a
# Device without a Property, the Client must assume all the Properties for that Device, and indeed the Device itself, are no
# longer available.

    def __init__(self, device, dproperty, **kwds):    # dproperty is used instead of property to avoid confusion with the Python 'property'
        "Delete the given property, or all if dproperty is None"
        self.device = device
        self.dproperty = dproperty
        super().__init__(**kwds)


class ParseProperty():

    "Parent to Text, Number, Switch, Lights, Blob types"

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
    "Parent to ParseText, etc.,"

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
        # and self.formatted_number
        self._number(child.text)
        super().__init__(child)

    def _number(self, value):
        """Splits the number into a negative flag and three sexagesimal parts
           then calls self._sexagesimal or self._printf to create the formatted string"""
        value = value.strip()
        self.value = value   # the raw value
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
            self._sexagesimal(negative, number_list)
        else:
            self._printf(negative, number_list)


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

        self.formatted_number = number


    def _printf(self, negative, number_list):
        "Create string of the number according to the given format"
        value = number_list[0] + (number_list[1]/60) + (number_list[2]/360)
        if negative:
            value = -1 * value
        self.formatted_number = self.format % value


    def __str__(self):
        "Returns the string of the number using the format value"
        return self.formatted_number



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





############ Function which receives the xml tree ###############

def receive_tree(root, rconn):
    "Receives the element tree root"
    devices = set()       # create a set of devices
    for child in root:
        if child.tag == "defTextVector":
            text_vector = ParseTextVector(child)
            devices.add(text_vector.device)
            print(text_vector.device, text_vector.name)
            print(str(text_vector))
        if child.tag == "defNumberVector":
            number_vector = ParseNumberVector(child)
            devices.add(number_vector.device)
            print(number_vector.device, number_vector.name)
            print(str(number_vector))
        if child.tag == "defSwitchVector":
            switch_vector = ParseSwitchVector(child)
            devices.add(switch_vector.device)
            print(switch_vector.device, switch_vector.name)
            print(str(switch_vector))
        if child.tag == "defLightVector":
            light_vector = ParseLightVector(child)
            devices.add(light_vector.device)
            print(light_vector.device, light_vector.name)
            print(str(light_vector))
    print(devices)









