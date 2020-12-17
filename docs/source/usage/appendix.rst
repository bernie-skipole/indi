Technical appendix - MQTT
=========================

The functions mqtttoredis and mqtttoport are 'client functions' -in that they connect from MQTT to clients.

The functions inditomqtt and driverstomqtt are 'driver functions' as they connect drivers to MQTT.


The client functions take data from the client and publish it to MQTT with topic "to_indi_topic/client_mqtt_id" where client_mqtt_id is the mqtt_id of the client function.

The actual strings used are set as arguments of the function, the above strings are illustrative only.

The driver function subscribes, either to "to_indi_topic/#" if it has an empty subscribe_list, or it subscribes to each "to_indi_topic/client_mqtt_id" for every client_mqtt_id in its subscribe_list.

The "/#" feature is an MQTT wildcard, indicating it will subscribe to all topics starting with "to_indi_topic" - and hence to all clients.

Therefore the driver function receives the data from the clients and passes it on to the drivers.


Similarly the driver function takes data from drivers, and publishes it with topic "from_indi_topic/driver_mqtt_id", where driver_mqtt_id is the mqtt_id of the driver function.

The client function subscribes, either to "from_indi_topic/#" if it has an empty subscribe_list, or it subscribes to each "from_indi_topic/driver_mqtt_id" for every driver_mqtt_id in its subscribe_list.

Therefore the client function receives the data from the drivers and passes it on to the clients.

Snooping
^^^^^^^^

The INDI protocol features a snooping ability, in which drivers can monitor data sent by other drivers. This is implemented in the functions inditomqtt and driverstomqtt.

These functions subscribe to "snoop_control_topic/#"

and also to "snoop_data_topic/driver_mqtt_id" where driver_mqtt_id is the driver function's own mqtt_id.


If a driver wishes to snoop on another it sends a getProperties request - this is a request to snoop other devices, or device properties. The function will publish this request on "snoop_control_topic/driver_mqtt_id" where driver_mqtt_id is the driver function's own mqtt_id.  As all driver functions subscribe to this, they will all receive it, and will record the source driver_mqtt_id, and will know what device and property it is snooping on.

Other driver functions, if connected to a driver that it now knows is of interest to other snooping functions, will, when it receives data from such a connected driver, publish it to topic "snoop_data_topic/driver_mqtt_id" where driver_mqtt_id in this case is the mqtt_id of the remote function (not its own mqtt_id).  The remote function, as described above, already subscribes to this, and therefore receives the data it wishes to snoop.


