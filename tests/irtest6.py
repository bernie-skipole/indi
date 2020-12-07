from indiredis import inditomqtt, indi_server, mqtt_server

# define the hosts/ports where servers are listenning, these functions return named tuples.

indi_host = indi_server(host='localhost', port=7624)
mqtt_host = mqtt_server(host='localhost', port=1883)

# blocking call which runs the service, communicating between indiserver and mqtt

inditomqtt(indi_host, 'indi_server01', mqtt_host)
