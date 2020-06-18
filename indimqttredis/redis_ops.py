

############
#
# redis_ops
#
##########


# redisserver is a named tuple with attributes: 'host', 'port', 'db', 'password', 'keyprefix'

import redis


_REDISCONNECTION = None

_KEYPREFIX = ''


def open_redis(redisserver):
    "Returns a connection to the redis database, on failure returns None"
    global _KEYPREFIX, _REDISCONNECTION
    _KEYPREFIX = redisserver.keyprefix
    try:
        if _REDISCONNECTION is None:
            # create a connection to redis
            _REDISCONNECTION = redis.StrictRedis(host=redisserver.host, port=redisserver.port, db=redisserver.db, password=redisserver.password, socket_timeout=5)
    except Exception:
        _REDISCONNECTION = None
    return _REDISCONNECTION
    

