.. _bom:

Bill of Materials
=================

This page will provide the bill of materials listing the materials and components necessary to build the BusKill cable.

Standard USB-A Cable
--------------------

The standard BusKill cable assumes USB type A.

+-------+-----------------------------+--------+-----+--------+----------------------------------------------+---------------------------+
| Index | Item                        | Cost * | Qty | Total  | Source **                                    | Notes                     |
+=======+=============================+========+=====+========+==============================================+===========================+
| 1     | Carabiner                   | 6      | 1   | 6      | `Amazon <carabiner1_>`_                      |                           |
+-------+-----------------------------+--------+-----+--------+----------------------------------------------+---------------------------+
| 2     | USB Drive                   | 5      | 1   | 5      | `Amazon <usbadrive1_>`_                      |                           |
+-------+-----------------------------+--------+-----+--------+----------------------------------------------+---------------------------+
| 3     | USB Extension Cable         | 6      | 1   | 6      | `Amazon <usba3mextension1_>`_                | | USB type A              |
|       |                             |        |     |        |                                              | | 1 meter length          |
+-------+-----------------------------+--------+-----+--------+----------------------------------------------+---------------------------+
| 4     | Magnetic Breakaway          | 10     | 1   | 10     | `Amazon <usbamagneticbreakaway1_>`_          |                           |
+-------+-----------------------------+--------+-----+--------+----------------------------------------------+---------------------------+

Grand Total: ~$30

.. figure:: /images/buskill_cable_usb_a.jpg
  :height: 300px
  :alt: image of the BusKill USB-A cable
  :align: center

  The standard USB-A BusKill cable. Source: `Michael Altfield's tech blog <https://tech.michaelaltfield.net/2020/01/02/buskill-laptop-kill-cord-dead-man-switch/>`_

USB-C Variant
-------------

If your device has USB type C ports and no USB type A ports, you can make a BusKill cable from the following USB-C components.

+-------+-----------------------------+--------+-----+--------+----------------------------------------------+---------------------------+
| Index | Item                        | Cost * | Qty | Total  | Source **                                    | Notes                     |
+=======+=============================+========+=====+========+==============================================+===========================+
| 1     | Carabiner                   | 6      | 1   | 6      | `Amazon <carabiner1_>`_                      |                           |
+-------+-----------------------------+--------+-----+--------+----------------------------------------------+---------------------------+
| 2     | USB Drive                   | 20     | 1   | 20     | `Amazon <usbcdrive1_>`_                      | USB type C                |
+-------+-----------------------------+--------+-----+--------+----------------------------------------------+---------------------------+
| 3     | USB Extension Cable         | 13     | 1   | 13     | `Amazon <usbc3mextension1_>`_                | | USB type C              |
|       |                             |        |     |        |                                              | | 1 meter length          |
+-------+-----------------------------+--------+-----+--------+----------------------------------------------+---------------------------+
| 4     | Magnetic Breakaway          | 25     | 1   | 25     | `Amazon <usbcmagneticbreakaway1_>`_          | USB type C                |
+-------+-----------------------------+--------+-----+--------+----------------------------------------------+---------------------------+

Grand Total: ~$65

TODO: picture

.. note:: While the BusKill cable has an open-source design, some of the individual components used to build the BusKill cable do not have open-source designs.

	To help make more of the BusKill cable's components open-source, please see our :ref:`wishlist`

\* all prices shown are in USD and are likely to change over time

** The BusKill project earns fees from qualifying purchases made through the Amazon Associates program. Please help our project stay alive by purchasing items through our affiliate links on this page.

.. enable affiliate links only if we're building to html so our links don't
.. end-up in offline material, which is a violation of the affiliate terms
.. affiliatelinks::

	https://www.amazon.com/gp/product/B01JHE50KY/ref=as_li_tl?ie=UTF8&tag=docsbuskill-20&camp=1789&creative=9325&linkCode=as2&creativeASIN=B01JHE50KY&linkId=61cdf51e8b72d43e9abc41e960827bf0 https://docs.buskill.in/buskill-app/en/stable/hardware_dev/bom.html usbadrive1

	https://www.amazon.com/gp/product/B01CGMV8AK/ref=as_li_tl?ie=UTF8&tag=docsbuskill-20&camp=1789&creative=9325&linkCode=as2&creativeASIN=B01CGMV8AK&linkId=35c660d0f78a69f0837e426d9c2b0582 https://docs.buskill.in/buskill-app/en/stable/hardware_dev/bom.html carabiner1

	https://www.amazon.com/gp/product/B0759FKCK8/ref=as_li_tl?ie=UTF8&tag=docsbuskill-20&camp=1789&creative=9325&linkCode=as2&creativeASIN=B0759FKCK8&linkId=89bb6c91a1a03512104978c10cffe293 https://docs.buskill.in/buskill-app/en/stable/hardware_dev/bom.html usbamagneticbreakaway1

	https://www.amazon.com/gp/product/B0002Y6CYM/ref=as_li_tl?ie=UTF8&tag=docsbuskill-20&camp=1789&creative=9325&linkCode=as2&creativeASIN=B0002Y6CYM&linkId=9b18bd89da3db1b4fd44402bee87da93 https://docs.buskill.in/buskill-app/en/stable/hardware_dev/bom.html usba3mextension1

	https://www.amazon.com/gp/product/B01GGKYXVE/ref=as_li_tl?ie=UTF8&tag=docsbuskill-20&camp=1789&creative=9325&linkCode=as2&creativeASIN=B01GGKYXVE&linkId=4aead1c57d3c13ad92a8ee43c0475e3f https://docs.buskill.in/buskill-app/en/stable/hardware_dev/bom.html usbctousba1

	https://www.amazon.com/gp/product/B01BY4MFEY/ref=as_li_tl?ie=UTF8&tag=docsbuskill-20&camp=1789&creative=9325&linkCode=as2&creativeASIN=B01BY4MFEY&linkId=008dc37c2e34b71d0687956d6a167272 https://docs.buskill.in/buskill-app/en/stable/hardware_dev/bom.html usbcdrive1

	https://www.amazon.com/gp/product/B07MCS2WWC/ref=as_li_tl?ie=UTF8&tag=docsbuskill-20&camp=1789&creative=9325&linkCode=as2&creativeASIN=B07MCS2WWC&linkId=20164822af30ec0d4b7b33dc454e0e78 https://docs.buskill.in/buskill-app/en/stable/hardware_dev/bom.html usbcmagneticbreakaway1

	https://www.amazon.com/gp/product/B07KR5PP91/ref=as_li_tl?ie=UTF8&tag=docsbuskill-20&camp=1789&creative=9325&linkCode=as2&creativeASIN=B07KR5PP91&linkId=8e9238d9f13cba94a6a5ec3073f28d2c https://docs.buskill.in/buskill-app/en/stable/hardware_dev/bom.html usbc3mextension1
