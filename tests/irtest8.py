from indiredis import mqtttoport, mqtt_server

# define the host port where the mqtt server is listenning, this function returns a named tuple.

mqtt_host = mqtt_server(host='localhost', port=1883)

# blocking call which runs the service,

mqtttoport("indi_client01", mqtt_host, port=7624)
