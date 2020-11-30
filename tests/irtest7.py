from indiredis import driverstomqtt, mqtt_server

# define the hosts/ports where servers are listenning, this function returns a named tuple.

mqtt_host = mqtt_server('indi_server01', host='localhost', port=1883)

# blocking call which runs the service, communicating between drivers and mqtt

driverstomqtt(["indi_simulator_telescope", "indi_simulator_ccd"], mqtt_host)
