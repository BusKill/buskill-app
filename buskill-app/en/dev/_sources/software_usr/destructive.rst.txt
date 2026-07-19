.. _destructive:

Destructive Triggers
====================

This section will describe how BusKill can be used to initiate destructive triggers.

Destructive triggers include triggers that are designed to cause damage to your data when BusKill is triggered, such as software self-destruct sequences.

Intentional Difficulty
----------------------

Some people are disappointed when they learn that the BusKill app doesn't include any self-destruct triggers. This is intentional. We raise the barrier of entry on destructive triggers because most people probably don't actually want an accidental false-positive to destroy all their data and

**We do not include destructive triggers in the BusKill app**, and we intentionally **make it difficult to use destructive triggers** with BusKill.

.. warning::

	The guides linked-to in this section contains experimental files, commands, and software. This information may or may not lead to corruption or total permanent deletion of some or all of your data. We've done our best to carefully guide the reader so they know the risks of each BusKill trigger, but we cannot be responsible for any data loss that has occurred as a result of following these guides.

	The contents of this documentation is provided openly and is licensed under the CC BY-SA license. The software is licensed under the GNU GPLv3 license. All content here is consistent with the limitations of liabilities outlined in its respective licenses.

	We highly recommend that any experiments with the scripts included in this article are used exclusively on a disposable machine containing no valuable data.

	If data loss is a concern for you, then leave now and do not proceed with following this guide. You have been warned.

LUKS
----

BusKill users who run Linux or QubesOS can configure BusKill with udev rules that will wipe the LUKS header, rendering your entire FDE Disks' data permanently inaccessible.

For more information on how to configure BusKill to trigger a LUKS Header Shredder, see the following article:

 * https://www.buskill.in/luks-self-destruct/

If you're running QubesOS, see our section on Qubes.

 * :ref:`qubes`
