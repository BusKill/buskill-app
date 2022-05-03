.. _usb_storage_initalization:

(optional) Initalize USB Storage
================================

This section will describe how format the USB storage drive and put the BusKill software on it.

.. note::
  The BusKill software cannot run on the USB drive. It must be run from your computer.

  As such, this is an **optional** step. It's documented here as a guide for how Alt Shift International prepares the USB Storage Drives when selling BusKill kits to customers. Having the software on the USB drive simply makes it easier for the end-user (so they can just copy the software from the USB drive to their computer instead of downloading it from the Internet).

  If you're building a BusKill cable for your own use, you should probably **skip this step and just** :ref:`Download the app <download_app>`.

Windows 10
----------

Step 1: Assemble Cable
^^^^^^^^^^^^^^^^^^^^^^

If you haven't yet, :ref:`assemble the BusKill cable <hardware_assembly>`

Step 2: Plug Into Computer
^^^^^^^^^^^^^^^^^^^^^^^^^^

Plug the assembled BusKill Cable (with the USB drive attached *through* the Magnetic breakaway) into your computer

.. figure:: /images/buskill_usb_storage_plug_in.jpg
  :alt: picture showing the fully-assembled BusKill cable with the USB Storage Drive connected to the magnetic breakaway connected to a laptop's USB port
  :align: center
  :target: ../_images/buskill_usb_storage_plug_in.jpg

.. note:: By plugging in the USB Storage Drive into the computer *via* the magnetic breakaway cable (as opposed to plugging the USB Storage Drive directly into the machine), you also verify the functionality of the cable's pinout.

Step 3: Format
^^^^^^^^^^^^^^

Open Windows Explorer (Start -> File Explorer)

.. figure:: /images/buskill_usb_storage_win_open_file_explorer.png
  :align: center

Click on "This PC"

.. figure:: /images/buskill_usb_storage_win_click_this_pc.png
  :align: center
        
Under "Devices and drives", right-click on the USB drive and choose "Format"

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

.. figure:: /images/buskill_usb_storage_win_format_options.png
  :align: center

.. note::
  Make sure the ``Volume label`` is ``BusKill`` with an upper-case ``B`` and ``K`` -- not ``Buskill`` nor ``buskill``.

Double-check that you've selected the **correct drive** before clicking ``OK`` in the WARNING prompt. If you proceed with formatting the wrong drive, it will immedetialy lead to **loss of all your data** on that drive.

.. figure:: /images/buskill_usb_storage_win_format_warning.png
  :align: center

After the format completes, close the windows.

.. figure:: /images/buskill_usb_storage_win_format_complete.png
  :align: center

In the File Explorer, you should now see a drive named ``BusKill``

.. figure:: /images/buskill_usb_storage_win_this_pc_now_says_buskill_label_on_drive.png
  :align: center

Step 4: Download, Verify, Extract Archive
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

   You only need to do ths step once. If you've already downloaded, verified, and extracted the archive to your computer, then skip this step

You should have already recieved:

1. A download link to the "usbRoot" compressed archive and
1. A SHA256 Hash for this file

Download the archive using the provided link and put it in your ``Downloads`` folder. This archive contains the files that will be extracted onto the newly formatted USB Storage Drive.
   
.. note:: Advanced users can build the .zip archive themselves using docker by checking out the git repo and executing the following script.

   * https://github.com/BusKill/buskill-app/blob/dev/build/usb/debianWrapper.sh

Open a new File Explorer Window (File -> New Window) and open your Downloads folder. Find the .zip archive.

.. list-table::

	* - .. figure:: /images/buskill_usb_storage_win_open_new_file_explorer_window.png
		:alt: screenshot shows how to open a new File Explorer Window (File -> New Window)
		:align: center
		:target: ../_images/buskill_usb_storage_win_open_new_file_explorer_window.png

	  - .. figure:: /images/buskill_usb_storage_win_click_downloads.png
		:alt: screenshot shows where to click "Downloads"
		:align: center
		:target: ../_images/buskill_usb_storage_win_click_downloads.png

Before extracting the archive's contents, check the integrity of the compressed archive via its SHA256 checksum. This is the "hash" or "checksum" that you should have recieved with the download link.

Check the integrity of the archive in PowerShell (Start -> Windows PowerShell).

.. figure:: /images/buskill_usb_storage_win_open_powershell.png
  :alt: screenshot shows how to open Windows PowerShell (Start -> PowerShell)
  :align: center
  :target: ../_images/buskill_usb_storage_win_open_powershell.png

Type the following command:

::

  Get-FileHash Downloads\buskill*.zip

.. figure:: /images/buskill_usb_storage_win_get_filehash.png
  :alt: screenshot shows the SHA256 output from the File-GetHash command
  :align: center
  :target: ../_images/buskill_usb_storage_win_get_filehash.png

Check that the ``Hash`` exactly matches the hash provided along with the download link.

.. warning::
  Do *not* proceed if the hash doesn't match.

  If the hash does not match, it's an indication that the compressed archive is corrupted. This means the **software won't work for the customer**, so this is a critical QA step.

If the hash matches, close the PowerShell window and extract its contents.

.. figure:: /images/buskill_usb_storage_win_close_powershell.png
  :alt: screenshot shows how to close the PowerShell window (click the "X")
  :align: center
  :target: ../_images/buskill_usb_storage_win_close_powershell.png

Right-click on the archive and click "Extract All..."

.. figure:: /images/buskill_usb_storage_win_extract_all.png
  :alt: screenshot shows 
  :align: center
  :target: ../_images/buskill_usb_storage_win_extract_all.png

Click "Extract"

.. figure:: /images/buskill_usb_storage_win_extract.png
  :alt: screenshot shows the "Extract Compressed (Zipped) Folders" wizard and highlights the "Extract" button to proceed
  :align: center
  :target: ../_images/buskill_usb_storage_win_extract.png

Step 4: Copy Files
^^^^^^^^^^^^^^^^^^

In the extracted archive's directory, enter the ``usbRoot`` directory.

Double-click ``usbRoot``

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

Under "This PC" select the ``BUSKILL`` USB Storage Drive and click ``Copy``

.. figure:: /images/buskill_usb_storage_win_copy_to_usb.png
  :alt: screenshot shows the "Copy Items" popup window and "BUSKILL" selected as the destination, with the "Copy" button selected
  :align: center
  :target: ../_images/buskill_usb_storage_win_copy_to_usb.png

When the copy finishes, close the top two File Explorer windows

.. list-table::

	* - .. figure:: /images/buskill_usb_storage_win_close_window_1.png
		:alt: screenshot shows three File Explorer windows with the "X" highlighted on the top-most window
		:align: center
		:target: ../_images/buskill_usb_storage_win_close_window_1.png

	  - .. figure:: /images/buskill_usb_storage_win_close_window_2.png
		:alt: screenshot shows two File Explorer windows with the "X" highlighted on the top-most window
		:align: center
		:target: ../_images/buskill_usb_storage_win_close_window_2.png

Step 4: Safely Eject
^^^^^^^^^^^^^^^^^^^^

Right-click on the ``BUSKILL`` USB Storage Drive and click ``Eject``

.. warning::

  Do *not* simply remove the USB Storage Drive from your computer without first ejecting it as shown above!!
 
  Physically removing the drive from the computer before clicking ``Eject`` can cause data to not be written, even after the copy finishes successfully.

  If the data isn't fully written to the disk before it's removed, the software on the USB Storage Drive could be corrupt. This means the **software won't work for the customer**, so this is a **critical QA step**.

After the drive is no longer visible, physically remove the USB Storage Drive.

.. figure:: /images/buskill_usb_storage_win_eject.png
  :alt: screenshot shows the right-click menu for the "BUSKILL" drive and the "Eject" option highlighted
  :align: center
  :target: ../_images/buskill_usb_storage_win_eject.png

Step 5: Verify Integrity
^^^^^^^^^^^^^^^^^^^^^^^^

Plug the BusKill Cable into the computer again.

.. figure:: /images/buskill_usb_storage_plug_in.jpg
  :alt: picture showing the fully-assembled BusKill cable with the USB Storage Drive connected to the magnetic breakaway connected to a laptop's USB port
  :align: center
  :target: ../_images/buskill_usb_storage_plug_in.jpg

Double-click the ``BUSKILL`` drive when it appears

        TODO: screenshot

Double-click `provision`

        TODO: screenshot

If the window says "FAIL," then something is wrong with the drive. Go back to the "Format" step above and retry.

If the window says "PASS" then everything worked. Safely eject the drive.

.. figure:: /images/buskill_usb_storage_win_eject.png
  :alt: screenshot shows the right-click menu for the "BUSKILL" drive and the "Eject" option highlighted
  :align: center
  :target: ../_images/buskill_usb_storage_win_eject.png

After the drive is no longer visible, physically remove the USB Storage Drive.

TODO: Step to verify the integrity of the data after it's written

 * https://superuser.com/questions/566113/does-windows-calculate-crcs-to-check-every-file-operation?rq=1
 * https://stackoverflow.com/questions/72087842/windows-equivalent-to-sha256sum-c-cryptographic-hash-digest-file-recursive
 * https://serverfault.com/questions/1099949/windows-equivalent-to-sha256sum-c-cryptographic-hash-digest-file-recursive
 * https://superuser.com/questions/1719053/windows-equivalent-to-sha256sum-c-cryptographic-hash-digest-file-recursive

Linux
-----

TODO

MacOS
-----

TODO
