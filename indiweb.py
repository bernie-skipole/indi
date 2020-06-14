#!/home/indi/indienv/bin/python3


"""Example script to run indiredis"""


from indimqttredis import indiredis

# define the servers

indi_server = indiredis.indi_server(host='localhost', port=7624)
redis_server = indiredis.redis_server(host='localhost', port=6379, db=0, password='')


# blocking call which runs the service, communicating between indiserver and redis

indiredis.run(indi_server, redis_server)
