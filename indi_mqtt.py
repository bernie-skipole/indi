#!/home/indi/indienv/bin/python3


# Alter the above shebang to point to your own Python location

"""Example script to run inditomqtt"""


from indiredis import inditomqtt, indi_server, mqtt_server

# define the hosts/ports where servers are listenning, these functions return named tuples.

indi_host = indi_server(host='localhost', port=7624)
mqtt_host = mqtt_server(host='10.34.167.1', port=1883, username='', password='', to_indi_topic='to_indi', from_indi_topic='from_indi')

# blocking call which runs the service, communicating between indiserver and MQTT

inditomqtt(indi_host, mqtt_host)


