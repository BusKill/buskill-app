.. _gui:

BusKill App: Graphical User Interface
=====================================

This page will describe how to use the BusKill app in GUI mode.

Arming
------

BusKill always starts in the disarmed state.

When BusKill is disarmed, events will never be triggered--even if the BusKill cable is unplugged.

.. figure:: /images/buskill_app_lin_arm2.gif
	:alt: Screenshot of BusKill in Linux
	:align: center
	:target: ../_images/buskill_app_lin_arm2.gif
	:width: 200 px

	Click the ``Arm`` button

To arm BusKill, click the ``Arm`` button. BusKill can be armed whether or not the cable is plugged-in. Plugging-in the BusKill cable never triggers any BusKill events, regardless of whether or not BusKill is armed or disarmed.

..
	Commenting-out this list-table block with captions until it doesn't break our PDF creator
	https://github.com/brechtm/rinohtype/issues/174

   list-table::

	* - .. figure:: /images/buskill_app_lin_disarmed1.jpg
		:alt: screenshot of the buskill-app in the disarmed state
		:align: center
		:target: ../_images/buskill_app_lin_disarmed1.jpg

		Linux
	  - .. figure:: /images/buskill_app_win_disarmed1.jpg
		:alt: screenshot of the buskill-app in the disarmed state
		:align: center
		:target: ../_images/buskill_app_win_disarmed1.jpg

		Windows
	  - .. figure:: /images/buskill_app_mac_disarmed1.jpg
		:alt: screenshot of the buskill-app in the disarmed state
		:align: center
		:target: ../_images/buskill_app_mac_disarmed1.jpg

		MacOS

.. list-table::

	* - .. figure:: /images/buskill_app_lin_disarmed1.jpg
		:alt: screenshot of the buskill-app in the disarmed state
		:align: center
		:target: ../_images/buskill_app_lin_disarmed1.jpg

	  - .. figure:: /images/buskill_app_win_disarmed1.jpg
		:alt: screenshot of the buskill-app in the disarmed state
		:align: center
		:target: ../_images/buskill_app_win_disarmed1.jpg

	  - .. figure:: /images/buskill_app_mac_disarmed1.jpg
		:alt: screenshot of the buskill-app in the disarmed state
		:align: center
		:target: ../_images/buskill_app_mac_disarmed1.jpg

Trigger Selector
^^^^^^^^^^^^^^^^

You can change what action the BusKill app takes when the BusKill cable is disconnected by changing the ``trigger`` setting.

To change the ``trigger`` setting, open the app menu and click ``Settings``.

.. list-table::

	* - .. figure:: /images/buskill_open_menu.png
		:alt: screenshot shows the app running with the hamburger menu in the top-left highlighted
		:align: center
		:target: ../_images/buskill_open_menu.png

	  - .. figure:: /images/buskill_settings_1.png
		:alt: screenshot shows the app running with the navigration drawer open, and the "Settings" option selected
		:align: center
		:target: ../_images/buskill_settings_1.png

Then click ``Trigger`` and select the action that you want to happen when the BusKill cable is disconnected (for example, "soft-shutdown")

.. list-table::

	* - .. figure:: /images/buskill_settings_trigger_1.png
		:alt: screenshot shows the app running on the Settings screen with a list of settings to configure
		:align: center
		:target: ../_images/buskill_settings_trigger_1.png

	  - .. figure:: /images/buskill_settings_trigger_2.png
		:alt: screenshot shows the app running with a list of triggers to select
		:align: center
		:target: ../_images/buskill_settings_trigger_2.png

.. note::

	Some triggers can be dangerous and cause data loss or data corruption. Please make sure you read the warning and accept the risk before choosing a given trigger.

	.. figure:: /images/buskill_trigger_warning.png
		:alt: screenshot shows a confiration dialog presented to the user asking them if they are sure they want to enable this trigger
		:align: center
		:target: ../_images/buskill_trigger_warning.png

Disarming
---------

When BusKill is armed, removing the BusKill cable will cause the screen to lock. Removing the cable does not disarm BusKill. Removing the cable subsequent times will continue to cause the screen lock trigger to be executed.

BusKill can be disarmed by closing the window or clicking the ``Disarm`` button.

..
	Commenting-out this list-table block with captions until it doesn't break our PDF creator
	https://github.com/brechtm/rinohtype/issues/174

   list-table::

	* - .. figure:: /images/buskill_app_lin_armed1.jpg
		:alt: screenshot of the buskill-app in the armed state
		:align: center
		:target: ../_images/buskill_app_lin_armed1.jpg

		Linux
	  - .. figure:: /images/buskill_app_win_armed1.jpg
		:alt: screenshot of the buskill-app in the armed state
		:align: center
		:target: ../_images/buskill_app_win_armed1.jpg

		Windows
	  - .. figure:: /images/buskill_app_mac_armed1.jpg
		:alt: screenshot of the buskill-app in the armed state
		:align: center
		:target: ../_images/buskill_app_mac_armed1.jpg

		MacOS

.. list-table::

	* - .. figure:: /images/buskill_app_lin_armed1.jpg
		:alt: screenshot of the buskill-app in the armed state
		:align: center
		:target: ../_images/buskill_app_lin_armed1.jpg

	  - .. figure:: /images/buskill_app_win_armed1.jpg
		:alt: screenshot of the buskill-app in the armed state
		:align: center
		:target: ../_images/buskill_app_win_armed1.jpg

	  - .. figure:: /images/buskill_app_mac_armed1.jpg
		:alt: screenshot of the buskill-app in the armed state
		:align: center
		:target: ../_images/buskill_app_mac_armed1.jpg

.. _gui_update:

Updating
--------

You can upgrade the BusKill app to the latest version within the app itself.

.. note::

  The update process is secure and censorship-resistant. First, it downloads a ``meta.json`` file (enumerating available releases) from a random mirror. If a new update is available, it downloads it to the same directory as your existing application. If the download was successful, it exits and launches the new version. If the new version launches successfully, it deletes the old version.

  All downloaded files (both the ``meta.json`` file and the portable application itself) are cryptographically signed with a 4096-bit RSA key. The PGP signature is checked immediately after download. If the signature is invalid, then the downloaded files are immediately wiped and the user is warned.

To update the app, open the app menu and click ``Update``.

.. list-table::

	* - .. figure:: /images/buskill_open_menu.png
		:alt: screenshot shows the app running with the hamburger menu in the top-left highlighted
		:align: center
		:target: ../_images/buskill_open_menu.png

	  - .. figure:: /images/buskill_update_1.png
		:alt: screenshot shows the app running with the navigration drawer open, and the "Update" option selected
		:align: center
		:target: ../_images/buskill_usb_update_1.png

.. warning::

  For privacy reasons, our software doesn't have any built-in `telemetry <https://en.wikipedia.org/wiki/Telemetry#Software>`_. If you select an action that will cause the software to query the Internet, we will inform you and ask for confirmation before proceeding.

  Though all file downloads are encrypted over https, your DNS lookups may not be encrypted. This means that someone eavesdropping on your internet connection may be able to see that you're using BusKill if you do an in-app update.

  Please consider using `encrypted DNS <https://en.wikipedia.org/wiki/DNS_over_HTTPS>`_, or a `VPN software <https://www.privacyguides.org/en/vpn/>`_ that tunnels your DNS requests.

The app will warn you that it is about to access the Internet, which could alert `Eve <https://en.wikipedia.org/wiki/Alice_and_Bob>`_ that you're using BusKill software (see above). If you accept these risks, click ``Check Update`` to proceed with checking for a new version of the app.

.. figure:: /images/buskill_update_2.png
  :alt: screenshot showing the app running with a modal titled "Check for Updates?" and the "Check Updates" button is highlighted
  :align: center
  :target: ../_images/buskill_update_2.png

Depending on your internet connection, the update could take several minutes to download.
