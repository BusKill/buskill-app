.. _3D_Print_Instructions:

Create a 3D-Printed BusKill
=================================

This section will describe from start to finish how to create a 3D printed BusKill. 

.. note::
  Example Note.

Bill of Materials
----------
Add BOM here.

Print the Parts
----------

Step 1: Get OpenSCAD file and create STL.
^^^^^^^^^^^^^^^^^^^^^^

Example Reference- If you haven't yet, :ref:`assemble the BusKill cable <hardware_assembly>`

Step 2: Prepare STL for Print
^^^^^^^^^^^^^^^^^^^^^^^^^^
        
Under ``Devices and drives``, right-click on the USB drive and choose ``Format``

.. figure:: /images/buskill_usb_storage_win_click_format.png
  :align: center

.. warning::
  Make absolutely sure you've selected the correct drive!!

  If you select the **wrong drive**, it may result in **irrevocable deletion of all your data!**

  If you're not sure, unplug the BusKill cable and plug it back in again. The drive will disappear and reappear. **Make absolutely sure you're choosing the BusKill USB Storage Drive** before proceeding with the format.

In the new window:

#. Set the ``File system`` to ``FAT32``
#. Leave the ``Allocation unit size`` at the default ``4096 bytes``
#. For ``Volume label``, type ``BusKill``
#. Leave the ``Quick Format`` option checked
#. Click ``Start``

.. figure:: /images/buskill_usb_storage_win_click_usbRoot.png
  :alt: screenshot shows the extracted archive's contents root with one folder titled "usbRoot"
  :align: center
  :target: ../_images/buskill_usb_storage_win_click_usbRoot.png

.. note ::
   Do not copy the ``usbRoot`` folder to the USB Storage Drive. Copy the *contents* of the ``usbRoot`` folder to the USB Storage Drive.

Click ``Home`` -> ``Select All``

.. figure:: /images/buskill_usb_storage_win_select_all.png
  :alt: screenshot shows the process to click Home -> Select All
  :align: center
  :target: ../_images/buskill_usb_storage_win_select_all.png

Click ``Home`` -> ``Copy to`` -> ``Choose location...``

.. figure:: /images/buskill_usb_storage_win_copy_to.png
  :alt: screenshot shows the process to click Home -> Copy to -> Choose location...
  :align: center
  :target: ../_images/buskill_usb_storage_win_copy_to.png

.. list-table::

	* - .. figure:: /images/buskill_usb_storage_win_pass.png
		:alt: screenshot shows how to close the command prompt window, with the "X" on the top-right highlighted
		:align: center
		:target: ../_images/buskill_usb_storage_win_pass.png

	  - .. figure:: /images/buskill_usb_storage_win_eject.png
		:alt: screenshot shows the right-click menu for the "BUSKILL" drive and the "Eject" option highlighted
		:align: center
		:target: ../_images/buskill_usb_storage_win_eject.png

Create the pogo connection
-----

Step 1: Create the Release pogo connection
^^^^^^^^^^^^^^^^^^^^^^

If you haven't yet, :ref:`assemble the BusKill cable <hardware_assembly>`

Step 2: Create the Breakaway pogo connection
^^^^^^^^^^^^^^^^^^^^^^^^^^
        
Under ``Devices and drives``, right-click on the USB drive and choose ``Format``

.. figure:: /images/buskill_usb_storage_win_click_format.png
  :align: center

.. warning::
  Make absolutely sure you've selected the correct drive!!

  If you select the **wrong drive**, it may result in **irrevocable deletion of all your data!**

  If you're not sure, unplug the BusKill cable and plug it back in again. The drive will disappear and reappear. **Make absolutely sure you're choosing the BusKill USB Storage Drive** before proceeding with the format.

In the new window:

#. Set the ``File system`` to ``FAT32``
#. Leave the ``Allocation unit size`` at the default ``4096 bytes``
#. For ``Volume label``, type ``BusKill``
#. Leave the ``Quick Format`` option checked
#. Click ``Start``

.. figure:: /images/buskill_usb_storage_win_click_usbRoot.png
  :alt: screenshot shows the extracted archive's contents root with one folder titled "usbRoot"
  :align: center
  :target: ../_images/buskill_usb_storage_win_click_usbRoot.png

.. note ::
   Do not copy the ``usbRoot`` folder to the USB Storage Drive. Copy the *contents* of the ``usbRoot`` folder to the USB Storage Drive.

Click ``Home`` -> ``Select All``

.. figure:: /images/buskill_usb_storage_win_select_all.png
  :alt: screenshot shows the process to click Home -> Select All
  :align: center
  :target: ../_images/buskill_usb_storage_win_select_all.png

Click ``Home`` -> ``Copy to`` -> ``Choose location...``

.. figure:: /images/buskill_usb_storage_win_copy_to.png
  :alt: screenshot shows the process to click Home -> Copy to -> Choose location...
  :align: center
  :target: ../_images/buskill_usb_storage_win_copy_to.png

.. list-table::

	* - .. figure:: /images/buskill_usb_storage_win_pass.png
		:alt: screenshot shows how to close the command prompt window, with the "X" on the top-right highlighted
		:align: center
		:target: ../_images/buskill_usb_storage_win_pass.png

	  - .. figure:: /images/buskill_usb_storage_win_eject.png
		:alt: screenshot shows the right-click menu for the "BUSKILL" drive and the "Eject" option highlighted
		:align: center
		:target: ../_images/buskill_usb_storage_win_eject.png

Insert pogo connection into case and connect to USB parts. 
-----
Step 1: Create Release 
^^^^^^^^^^^^^^^^^^^^^^

If you haven't yet, :ref:`assemble the BusKill cable <hardware_assembly>`

Step 2: Create Breakaway
^^^^^^^^^^^^^^^^^^^^^^^^^^
        
Under ``Devices and drives``, right-click on the USB drive and choose ``Format``

.. figure:: /images/buskill_usb_storage_win_click_format.png
  :align: center

.. warning::
  Make absolutely sure you've selected the correct drive!!

  If you select the **wrong drive**, it may result in **irrevocable deletion of all your data!**

  If you're not sure, unplug the BusKill cable and plug it back in again. The drive will disappear and reappear. **Make absolutely sure you're choosing the BusKill USB Storage Drive** before proceeding with the format.

In the new window:

#. Set the ``File system`` to ``FAT32``
#. Leave the ``Allocation unit size`` at the default ``4096 bytes``
#. For ``Volume label``, type ``BusKill``
#. Leave the ``Quick Format`` option checked
#. Click ``Start``

.. figure:: /images/buskill_usb_storage_win_click_usbRoot.png
  :alt: screenshot shows the extracted archive's contents root with one folder titled "usbRoot"
  :align: center
  :target: ../_images/buskill_usb_storage_win_click_usbRoot.png

.. note ::
   Do not copy the ``usbRoot`` folder to the USB Storage Drive. Copy the *contents* of the ``usbRoot`` folder to the USB Storage Drive.

Click ``Home`` -> ``Select All``

.. figure:: /images/buskill_usb_storage_win_select_all.png
  :alt: screenshot shows the process to click Home -> Select All
  :align: center
  :target: ../_images/buskill_usb_storage_win_select_all.png

Click ``Home`` -> ``Copy to`` -> ``Choose location...``

.. figure:: /images/buskill_usb_storage_win_copy_to.png
  :alt: screenshot shows the process to click Home -> Copy to -> Choose location...
  :align: center
  :target: ../_images/buskill_usb_storage_win_copy_to.png

.. list-table::

	* - .. figure:: /images/buskill_usb_storage_win_pass.png
		:alt: screenshot shows how to close the command prompt window, with the "X" on the top-right highlighted
		:align: center
		:target: ../_images/buskill_usb_storage_win_pass.png

	  - .. figure:: /images/buskill_usb_storage_win_eject.png
		:alt: screenshot shows the right-click menu for the "BUSKILL" drive and the "Eject" option highlighted
		:align: center
		:target: ../_images/buskill_usb_storage_win_eject.png

Test
-----

Step 1: See whether computer detects your drive
^^^^^^^^^^^^^^^^^^^^^^

If you haven't yet, :ref:`assemble the BusKill cable <hardware_assembly>`

Add glue and screw on the lid
-----

Step 1: See whether computer detects your drive
^^^^^^^^^^^^^^^^^^^^^^

If you haven't yet, :ref:`assemble the BusKill cable <hardware_assembly>`


