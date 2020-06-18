

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


class ParsedelProperty()

# A Device may tell a Client a given Property is no longer available by sending delProperty. If the command specifies only a
# Device without a Property, the Client must assume all the Properties for that Device, and indeed the Device itself, are no
# longer available.

    def __init__(self, device, dproperty, **kwds):    # dproperty is used instead of property to avoid confusion with the Python 'property'
        "Delete the given property, or all if dproperty is None"
        self.device = device
        self.dproperty = dproperty
        super().__init__(**kwds)


class ParseItem():

    "Parent to Text, Number, Switch, Lights, Blob types"

    def __init__(self, name, label, permission, state, timeout, **kwds):
        "Parent Item"
        self.name = name
        self.label = label
        self.state = state              # Idle, OK, Busy or Alert
        self.timemout = timeout          # The worst-case time it might take to change the value to something else
        self._set_permission(permission)
        super().__init__(**kwds)

    def _set_permission(self, permission):
        "Sets the possible permissions, Read-Only, Write-Only or Read-Write"
        if permission in ('ro', 'wo', 'rw'):
            self.permission = permission
        else:
            self.permission = 'ro'
        


    def elements(self):
        "Elements have name, value and label"
        element_values = {}
        element_labels = {}

    # To inform a Client of new current values for a Property and their state, a Device sends one settype element. It is only
    # required to send those members of the vector that have changed.

    def settype(self, values):
        "elements:values that have changed"
        pass




class ParseText(ParseItem):


    def __init__(self, value, **kwds):
        "The value is the string"
        self.value = value
        super().__init__(**kwds)




class ParseNumber(ParseItem):

    def __init__(self, value, nformat, **kwds):  # nformat is used instead of format to avoid confusion with Python 'format'
        "The value is the number"
        self.value = value
        self.nformat = nformat
        super().__init__(**kwds)



class ParseSwitch(ParseItem):


    def __init__(self, value, **kwds):
        "The value is On or Off"
        self.value = value
        super().__init__(**kwds)

    def _set_permission(self, permission):
        "Sets the possible permissions, Read-Only or Read-Write"
        if permission in ('ro', 'rw'):
            self.permission = permission
        else:
            self.permission = 'ro'



class ParseLights(ParseItem):

    def __init__(self, value, **kwds):
        "The value is Idle, OK, Busy or Alert"
        self.value = value
        super().__init__(**kwds)

    def _set_permission(self, permission):
        "Sets the permissions, Read-Only"
        self.permission = 'ro'



class ParseBlob(ParseItem):

    def __init__(self, value, **kwds):
        "The value is Idle, OK, Busy or Alert"
        self.value = value
        super().__init__(**kwds)

