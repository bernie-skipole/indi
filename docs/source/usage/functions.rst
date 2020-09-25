The indiredis package
=====================

.. automodule:: indiredis

Functions in indiredis
^^^^^^^^^^^^^^^^^^^^^^

These first three functions are used to create named tuples gathering the data for the
associated servers.

.. autofunction:: indiredis.indi_server

.. autofunction:: indiredis.redis_server

.. autofunction:: indiredis.mqtt_server

The tuples created by the above functions are then used as parameters for the following functions.

.. autofunction:: indiredis.inditoredis

For further information on the log_lengths parameter see :ref:`log_lengths`.

So a minimal script using defaults to run inditoredis could be::

    from indiredis import inditoredis, indi_server, redis_server

    # define the hosts/ports where servers are listenning, these functions return named tuples
    # which are required as arguments to inditoredis().

    indi_host = indi_server(host='localhost', port=7624)
    redis_host = redis_server(host='localhost', port=6379)

    # blocking call which runs the service, communicating between indiserver and redis

    inditoredis(indi_host, redis_host)

The two functions below work together to provide communications via an MQTT server.

.. autofunction:: indiredis.inditomqtt

.. autofunction:: indiredis.mqtttoredis

indiwsgi
^^^^^^^^
.. automodule:: indiredis.indiwsgi

An example with the Waitress web server is given at :ref:`web_client`.

This example requires Python3 packages skipole, waitress and redis, available from Pypi.

This particular client is general purpose, and learns all instrument properties from the redis store,
it employs a browser client refresh every ten seconds, and so may not be useful for an instrument that
updates data at a faster rate.

.. autofunction:: indiredis.indiwsgi.make_wsgi_app


