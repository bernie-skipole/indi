.. _tools:

Tools
=====

.. automodule:: indiredis.tools

.. autofunction:: indiredis.tools.open_redis

Reading values
^^^^^^^^^^^^^^

.. autofunction:: indiredis.tools.last_message

.. autofunction:: indiredis.tools.devices

.. autofunction:: indiredis.tools.properties

.. autofunction:: indiredis.tools.elements

.. autofunction:: indiredis.tools.attributes_dict

.. autofunction:: indiredis.tools.elements_dict

.. autofunction:: indiredis.tools.property_elements

Reading logs
^^^^^^^^^^^^

This function reads logs from the logdata key stores. See :ref:`logs`.

.. autofunction:: indiredis.tools.logs

.. _sending:

Sending values
^^^^^^^^^^^^^^

The following functions create the XML elements, and uses redis to publish the XML on the to_indi_channel.
This is picked up by the inditoredis process (which subscribes to the to_indi_channel), and
which then transmits the xml on to indisserver.

.. autofunction:: indiredis.tools.getProperties

.. autofunction:: indiredis.tools.newswitchvector

.. autofunction:: indiredis.tools.newtextvector

.. autofunction:: indiredis.tools.newnumbervector

.. autofunction:: indiredis.tools.enableblob

Utilities
^^^^^^^^^

.. autofunction:: indiredis.tools.number_to_float

.. autofunction:: indiredis.tools.format_number

.. autofunction:: indiredis.tools.clearredis

The clearredis function is called when inditoredis is started, and deletes all current redis keys, so if you wish to store logs you must implement your own process to copy data from the redis store.

clearredis does not delete the BLOBs folder or contents.



