#!/home/indi/indienv/bin/python3


# Alter the above shebang to point to your own Python location

"""Example script to run indiredis"""


from indimqttredis import indiredis

# define the hosts/ports where servers are listenning

indi_host = indiredis.indi_server(host='localhost', port=7624)
redis_host = indiredis.redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_')

# blocking call which runs the service, communicating between indiserver and redis

indiredis.run(indi_host, redis_host)


