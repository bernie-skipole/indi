Tools
=====

.. automodule:: indiredis.tools

.. autofunction:: indiredis.tools.open_redis

Reading properties
^^^^^^^^^^^^^^^^^^

.. autofunction:: indiredis.tools.last_message

.. autofunction:: indiredis.tools.devices

.. autofunction:: indiredis.tools.properties

.. autofunction:: indiredis.tools.elements

.. autofunction:: indiredis.tools.attributes_dict

.. autofunction:: indiredis.tools.elements_dict

.. autofunction:: indiredis.tools.property_elements

.. autofunction:: indiredis.tools.logs

Sending values
^^^^^^^^^^^^^^


The following functions create the XML elements, and uses redis to publish the XML on the to_indi_channel.
This is picked up by the inditoredis process (which subscribes to the to_indi_channel), and
which then transmits the xml on to indisserver.

.. autofunction:: indiredis.tools.getProperties

.. autofunction:: indiredis.tools.newswitchvector

.. autofunction:: indiredis.tools.newtextvector

.. autofunction:: indiredis.tools.newnumbervector

.. autofunction:: indiredis.tools.clearredis


