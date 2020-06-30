!/home/indi/indienv/bin/python3


# Alter the above shebang to point to your own Python location

"""Example script to run a redis client to test indiredis

This assumes indiserver is running with the telescope simulator"""


###  Device ###
### 'Telescope Simulator'

###  Properties ###
### 'ACTIVE_DEVICES', 'CONFIG_PROCESS', 'CONNECTION', 'CONNECTION_MODE', 'DEBUG', 'DEVICE_AUTO_SEARCH', 'DEVICE_BAUD_RATE', 'DEVICE_PORT', 'DEVICE_PORT_SCAN'
### 'DOME_POLICY', 'DRIVER_INFO', 'POLLING_PERIOD', 'SCOPE_CONFIG_NAME', 'TELESCOPE_INFO'


from indiredis import redis_server



def _open_redis(redisserver):
    "Opens a redis connection"
    # create a connection to redis
    rconn = redis.StrictRedis(host=redisserver.host,
                              port=redisserver.port,
                              db=redisserver.db,
                              password=redisserver.password,
                              socket_timeout=5)
    return rconn



def to_indi(message):
    data = message['data'])
    print("To INDI:")
    print(data)


def from_indi(message):
    data = message['data'])
    print("Form INDI")
    print(data)


if __name__ == "__main__":

    redisserver = redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_',
                          to_indi_channel='to_indi', from_indi_channel='from_indi')

    rconn = _open_redis(redisserver)

    ps = rconn.pubsub(ignore_subscribe_messages=True)

    # subscribe with handlers
    ps.subscribe(redisserver.to_indi_channel = to_indi,
                 redisserver.from_indi_channel = from_indi)


    # blocks and listens to redis
    while True:
        message = ps.get_message()
        if message:
            print(message)
        time.sleep(0.1)



    # tests

    # x = readvector(rconn, 'Telescope Simulator', 'ACTIVE_DEVICES')
    # print(f"{x.label}\n{x}")
    
