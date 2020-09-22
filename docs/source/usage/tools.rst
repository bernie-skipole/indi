Tools
=====

.. automodule:: indiredis.tools

Your script could start with::

    from indiredis import redis_server, tools

    redisserver = redis_server(host='localhost', port=6379)
    rconn = tools.open_redis(redisserver)

and then using rconn and redisserver you could call upon the functions provided here.

Where a timestamp is specified, it will be a string according to the INDI v1.7 white paper which describes it as::

    A timeValue shall be specified in UTC in the form YYYY-MM-DDTHH:MM:SS.S. The final decimal and subsequent
    fractional seconds are optional and may be specified to whatever precision is deemed necessary by the transmitting entity.
    This format is in general accord with ISO 86015 and the Complete forms defined in W3C Note "Date and Time Formats"

.. autofunction:: indiredis.tools.open_redis

.. autofunction:: indiredis.tools.last_message

.. autofunction:: indiredis.tools.getProperties







