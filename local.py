#!/home/indi/indienv/bin/python3


# Alter the above shebang to point to your own Python location

"""Example script to run mqtttoredis"""


from indiredis import mqtttoredis, mqtt_server, redis_server

# define the hosts/ports where servers are listenning, these functions return named tuples.

mqtt_host = mqtt_server(host='10.34.167.1', port=1883, username='', password='', to_indi_topic='to_indi', from_indi_topic='from_indi')
redis_host = redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_')

# blocking call which runs the service, communicating between mqtt and redis

mqtttoredis(mqtt_host, redis_host)



