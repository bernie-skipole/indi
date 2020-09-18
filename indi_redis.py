

"""Example script to run inditoredis"""


from indiredis import inditoredis, indi_server, redis_server

# define the hosts/ports where servers are listenning, these functions return named tuples
# which are required as arguments to inditoredis().

indi_host = indi_server(host='localhost', port=7624)
redis_host = redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_',
                          to_indi_channel='to_indi', from_indi_channel='from_indi')


# blocking call which runs the service, communicating between indiserver and redis

inditoredis(indi_host, redis_host)


