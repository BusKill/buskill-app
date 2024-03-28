.. _support:

Support
=======

As an open-source project, we try to keep all of our support requests on GitHub. If you

#. have a question that is not answered by this documentation,
#. discover a bug in the software, or
#. would like to request a feature in the software

then please `create an issue <https://github.com/BusKill/buskill-app/issues/new/choose>`_ on our GitHub.

If your bug is security-related and you'd like to contact us confidentially, please see :ref:`Reporting Security Bugs <securityreports>`

If you don't want to register for an account on GitHub or you'd like to remain anonymous, then you can `email us <https://www.buskill.in/contact/>`_. We'll put the issue on GitHub for you.

Bug Reports
-----------
In order for us to fix your bug, we need you to tell us:

#. What you expected to happen
#. What actually happened
#. Steps to Reproduce the bug
#. Your Debug Log
#. A Screenshot of the bug

For privacy reasons, our software doesn't have any built-in `telemetry <https://en.wikipedia.org/wiki/Telemetry#Software>`_ to report crashes or bugs. As such, we'll need you to tell us a bit about your system and what you did to cause the bug (so we can reproduce it).

If you'd like to help troubleshoot the bug yourself, you may find the `sourcecode <https://github.com/BusKill/buskill-app/tree/master/src>`_ and :ref:`sourcecode documentation <autodoc>` to be helpful.

.. _debug_log:

Debug Log
---------

The best way for us to understand the issue is for you to add your ``Debug Log`` to your Bug Report. This can be obtained in the app.

Step 1: Reproduce Bug
^^^^^^^^^^^^^^^^^^^^^

First, reproduce the bug before you attempt to fetch the ``Debug Log``. The ``Debug Log`` may not have the information we need if you don't copy it *after* encountering the bug.

Step 2: Copy Debug Log
^^^^^^^^^^^^^^^^^^^^^^

After the app malfunctions, open the app menu and click ``Debug Log``.

.. list-table::

	* - .. figure:: /images/buskill_open_menu.png
		:alt: screenshot shows the app running with the hamburger menu in the top-left highlighted
		:align: center
		:target: ../_images/buskill_open_menu.png

	  - .. figure:: /images/buskill_debug_log_1.png
		:alt: screenshot shows the app running with the navigration drawer open, and the "Debug Log" option selected
		:align: center
		:target: ../_images/buskill_usb_debug_log_1.png

Then click click the ``Copy Log`` button.

.. list-table::

	* - .. figure:: /images/buskill_debug_log_2.png
		:alt: screenshot shows the app running on the "Debug Log" screen with the button titled "Copy Log" highlighted
		:align: center
		:target: ../_images/buskill_debug_log_2.png

	  - .. figure:: /images/buskill_debug_log_3.png
		:alt: screenshot shows the app running on the "Debug Log" screen with a pop-up modal that says "The full Debug Log has been copied to your clipboard."
		:align: center
		:target: ../_images/buskill_usb_debug_log_3.png

Now you can paste the contents of your clipboard into the Bug Report on GitHub or send it in your email to us. Before publishing it on the Internet, you may want to obfuscate/redact your system's username if you wish to remain anonymous.

