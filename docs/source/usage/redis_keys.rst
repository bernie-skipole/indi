Redis Keys
==========

This section lists the keys used to store data in the redis database, and describes the data stored at that key. The keys can be set with a prefix string to avoid clashing with other keys you may be using.

The < > characters used below in the key names, refers to multiple values, so key properties:<devicename> will actually be multiple keys of the format "properties:device1", "properties:device2", etc.

If a key prefix is defined, then the full keynames will be "prefixproperties:device1", "prefixproperties:device2", etc.

NOTE : BLOB's are not stored in redis, but are held in the BLOB folder given as an argument to indiredis.

Timestamps of sent requests
^^^^^^^^^^^^^^^^^^^^^^^^^^^

These timestamps are saved so that a client can resend a getProperties if one has not been sent for a period. May be useful if a client has been disconnected for a while.

**getProperties**

Contains a timestamp updated whenever the client sends the general getProperties command.

**getProperties:device:<devicename>**

Contains a timestamp updated whenever the client sends the getProperties command with a specified device.

**getProperties:property:<propertyname>:<devicename>**

Contains a timestamp updated whenever the client sends the getProperties command with a specified device and property.

Stored current values
^^^^^^^^^^^^^^^^^^^^^

**devices**

A set of device names.

**properties:<devicename>**

A key is created for each device name, for example, properties:telescope, properties:dome, etc., Each stores a set of property names for that particular device.

**attributes:<propertyname>:<devicename>**

A key is created for every property name, for every device name. Each key stores a hash table of attributes:values for that property, device.

**messages**

Stores a string of "timestamp space message" for the last message received without a specified device. The timestamp is that provided by the protocol.

**devicemessages:<devicename>**

A key is created for each device name. Each key stores a string of "timestamp space message" for the last message received for the device.

**elements:<propertyname>:<devicename>**

A key is created for every property name, for every device name. Each key stores a set of element names for the device property.

**elementattributes:<elementname>:<propertyname>:<devicename>**

A key is created for every element name, for every property name, for every device name. Each key stores a hash table of attributes:values for the element.

.. _logs:

Stored logged values
^^^^^^^^^^^^^^^^^^^^

As well as the current values stored above, as values change, a history of data is stored within keys listed here. Each log is stored as a list of strings, each string being of the format Timestamp space datastring.  This Timestamp is the time at which the data was received (Not timestamps given in the protocol - though they will be included within the data string where given). The datastrings are JSON strings of the data.

**logdata:devices**

Each datastring is a JSON list of device names. This rarely changes during normal operation, but new logs will be created as new devices are defined, and as devices are deleted. Therefore each log will be a string of the format "Timestamp [device1, device2, ...]" and as new logs are created LPUSH is used to add to the list. Use LINDEX logdata:devices 0 to obtain the most recent log entry.

**logdata:properties:<devicename>**

A key is created for each device name. The datastring for each log is a JSON string of the property list for the device.

**logdata:attributes:<propertyname>:<devicename>**

A key is created for every property name, for every device name. The datastring for each log is a JSON string of an attribute object for the given property and device.

**logdata:messages**

Each datastring is a JSON string of the list [timestamp, message] for messages received without a specified device. Therefore each log will be of the format "Timestamp [timestamp, message]" where the first Timestamp is the time at which the message is received, and the message timestamp is that given within the indi protocol.

**logdata:devicemessages:<devicename>**

A key is created for each device name. Each datastring is a JSON string of the list [timestamp, message] for messages received for the device.

**logdata:elements:<propertyname>:<devicename>**

A key is created for every property name, for every device name. The datastring for each log is a JSON string of the element names for the device property.

**logdata:elementattributes:<elementname>:<propertyname>:<devicename>**

A key is created for every element name, for every property name, for every device name. Each key stores a a JSON string of an attribute object for the element.

.. _log_lengths:

Log Lengths
^^^^^^^^^^^

When using the function inditoredis, the arguments are:

inditoredis(indiserver, redisserver, log_lengths, blob_folder)

The log_lengths is a dictionary, of the form::

    log_lengths = {
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

 
If log_lengths is not given, the above defaults are used. The above indicates 5 logs will be retained in the list stored within logdata:devices, but 50 logs will be retained within logdata:elementattributes:<elementname>:<propertyname>:<devicename> where the property is a numbervector. Thus a log of the last 50 numbers are stored, as a history of number changes is more likely to be useful.

Property Attributes
^^^^^^^^^^^^^^^^^^^

The keys attributes:<propertyname>:<devicename> each hold a hash table of attributes of the property. For all properties this is:

    * device : name of device
    * name : name of property
    * state : one of Idle, Ok, Busy or Alert
    * perm : one of 'ro', 'wo', 'rw'
    * label : GUI label for the property
    * group : group label which gathers properties under headings
    * timestamp : timestamp given with the property
    * vector : Type of property, one of TextVector, NumberVector, SwitchVector, LightVector, BLOBVector

All properties, apart from LightVector also have:

    * timeout : worse-case time to affect

For the SwitchVector, an added value is:

    * rule : one of OneOfMany, AtMostOne, AnyOfMany

For the BlobsVector, an added value is:

    * blobs : one of Enabled, Disabled

Enabled means that, for this property, setBLOBVector tags containing BLOB data may arrive on this connection, Disabled means they should not be received, though it is still possible for BLOBS to arrive via some other process.
    

Element Attributes
^^^^^^^^^^^^^^^^^^

The keys elementattributes:<elementname>:<propertyname>:<devicename> hold a hash table of attributes of the element. For all elements apart from Blob elements this is:

    * name : name of the element
    * label : GUI label for the element
    * value : the actual value of the element, i.e. the text for an element of a TextVector

A Blob element has name and label, but not value.

For a number element of a NumberVector, additional fields are:

    * format : A format string, defining how the number should appear
    * formatted_number : The value, formatted as per the format string
    * float_number : The value as a float (parsed from sexagesimal if necessary)
    * min : minimal value
    * float_min : The minimal value as a float
    * max : maximum value, ignore if min == max
    * float_max : The maximum value as a float
    * step : allowed increments, ignore if 0
    * float_step : The step value as a float

Note: as the INDI specification allows various formats for the number value, and for min, max and step values, as well as storing the originals, float values are also stored for each value.

If receiving Blobs are enabled, Blob elements have fields:

    * name : name of the element
    * label : GUI label for the element
    * format : format as a file suffix, eg: .z, .fits, .fits.z
    * size : number of bytes in decoded and uncompressed BLOB
    * filepath : path of the file where the Blob has been saved.
    * timestamp : The same timestamp as given in the BlobsVector


Redis pubsub
^^^^^^^^^^^^

As data is received, as well as being parsed and stored in the redis keys described above, the received XML string is published on the from_indi_channel defined when calling the redis_server function. A logging or diagnostic process can therefore have access to the received XML by subscribing to this channel.

The client can transmit XML data towards indiserver by publishing the required XML on the to_indi_channel.  Alternatively, Python functions which specifically send number, text, etc., values are available in the tools module, described at :ref:`sending`.

