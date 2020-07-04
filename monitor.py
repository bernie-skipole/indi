#!/home/indi/indienv/bin/python3


# Alter the above shebang to point to your own Python location

"""Example script to run a redis client to test indiredis

This assumes indiserver is running with the telescope simulator"""


###  Device ###
### 'Telescope Simulator'

###  Properties ###
### 'ACTIVE_DEVICES', 'CONFIG_PROCESS', 'CONNECTION', 'CONNECTION_MODE', 'DEBUG', 'DEVICE_AUTO_SEARCH', 'DEVICE_BAUD_RATE', 'DEVICE_PORT', 'DEVICE_PORT_SCAN'
### 'DOME_POLICY', 'DRIVER_INFO', 'POLLING_PERIOD', 'SCOPE_CONFIG_NAME', 'TELESCOPE_INFO'

from time import sleep

import redis

from indiredis import redis_server, fromxml



def _open_redis(redisserver):
    "Opens a redis connection"
    # create a connection to redis
    rconn = redis.StrictRedis(host=redisserver.host,
                              port=redisserver.port,
                              db=redisserver.db,
                              password=redisserver.password,
                              socket_timeout=5)
    return rconn


class To_INDI():

    def __init__(self, rconn):
        self.rconn = rconn

    def __call__(self, message):
        data = message['data']
        print("To INDI:")
        print(data)


class From_INDI():

    def __init__(self, rconn):
        self.rconn = rconn

    def __call__(self, message):
        data = message['data']
        print("From INDI")
        print(data)

        if data == b"defTextVector:ACTIVE_DEVICES:Telescope Simulator":
            x = fromxml.readvector(rconn, 'Telescope Simulator', 'ACTIVE_DEVICES')
            print(f"{x.label}\n{x}")


if __name__ == "__main__":

    redisserver = redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_',
                          to_indi_channel='to_indi', from_indi_channel='from_indi')


    fromxml.setup_redis(redisserver.keyprefix, redisserver.to_indi_channel, redisserver.from_indi_channel)

    rconn = _open_redis(redisserver)

    ps = rconn.pubsub(ignore_subscribe_messages=True)

    to_indi = To_INDI(rconn)
    from_indi = From_INDI(rconn)

    # subscribe with handlers
    ps.subscribe(**{redisserver.to_indi_channel:to_indi,
                    redisserver.from_indi_channel:from_indi})


    # blocks and listens to redis
    while True:
        message = ps.get_message()
        if message:
            print(message)
        sleep(0.1)

