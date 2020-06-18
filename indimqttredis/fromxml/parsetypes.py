

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


class delProperty()

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

    def __init__(self, **kwds):
        "Parent Item"
        # Required properties
        self.device = kwds.pop("device")    # name of Device
        self.name = kwds.pop("name")        # name of Property
        self.state = kwds.pop("state")      # current state of Property; Idle, OK, Busy or Alert

        # implied properties
        self.label = kwds.pop("label", name)   # GUI label, use name by default
        self.group = kwds.pop("group", "")     # Property group membership, blank by default
        self.timestamp = kwds.pop("timestamp", 0) # moment when these data were valid
                                                  ###### # set the default to a real timestamp  ##############!!!!!
        self.message = kwds.pop("message", "")

        if kwds:
            kwds.clear()                      # remove any unknown arguments, remove if further parent classes are to be used

        super().__init__(**kwds)


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


class ParseElement():
    "Parent to ParseText, etc.,"

    def __init__(self, **kwds):
        self.name = kwds.pop("name")           # name of the element, required value
        self.label = kwds.pop("label", name)   # GUI label, use name by default
        if kwds:
            kwds.clear()                       # remove any unknown arguments, remove if further parent classes are to be used
        super().__init__(**kwds)



################ Text ######################

class ParseTextVector(ParseProperty):

    def __init__(self, value, **kwds):
        "The value is the xml defTextVector, **kwds are its attributes"
        perm = kwds.pop("perm")
        self._set_permission(perm)              # ostensible Client controlability
        self.timeout = kwds.pop("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        self.elements(value)                
        super().__init__(**kwds)

    def elements(self, value):
        "value is the xml defTextVector, this sets its child elements"
        self.element_list = []
        for child in value:
            text_element = ParseText(child.text, **child.attrib)
            self.element_list.append(text_element)

    def __str__(self):
        "Creates a string of label:text lines"
        for element in self.element_list:
            print(str(element)+"/n")



class ParseText(ParseElement):
    "text items contained in a ParseTextVector"

    def __init__(self, value, **kwds):
        self.value = value
        super().__init__(**kwds)

    def __str__(self):
        return f"{self.label} : {self.value}"



################ Number ######################

class ParseNumberVector(ParseProperty):

    def __init__(self, value, **kwds):
        "The value is the number"
        perm = kwds.pop("perm")
        self._set_permission(perm)              # ostensible Client controlability
        self.timeout = kwds.pop("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        self.value = value
        super().__init__(**kwds)



################ Switch ######################

class ParseSwitchVector(ParseProperty):


    def __init__(self, value, **kwds):
        "The value is On or Off"
        perm = kwds.pop("perm")
        self._set_permission(perm)              # ostensible Client controlability
        self.timeout = kwds.pop("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        self.value = value
        super().__init__(**kwds)

    def _set_permission(self, permission):
        "Sets the possible permissions, Read-Only or Read-Write"
        if permission in ('ro', 'rw'):
            self.permission = permission
        else:
            self.permission = 'ro'


################ Lights ######################

class ParseLightVector(ParseProperty):

    def __init__(self, value, **kwds):
        "The value is Idle, OK, Busy or Alert"
        self.permission = 'ro'                      # permission always Read-Only
        self.value = value
        super().__init__(**kwds)


        

################ BLOB ######################

class ParseBLOBVector(ParseProperty):

    def __init__(self, value, perm, **kwds):
        "The value is Idle, OK, Busy or Alert"
        self._set_permission(perm)      # ostensible Client controlability
        self.value = value
        self.timeout = kwds.pop("timeout", 0)   # worse-case time to affect, 0 default, N/A for ro
        super().__init__(**kwds)




def receive_tree(root, rconn):
    "Receives the element tree root"
    for child in root:
        if child.tag == "defTextVector":
            text_vector = ParseTextVector(child, **child.attrib)
            print(text_vector.device, text_vector.name)
            print(str(text_vector))











