.. _manpage:

============
 BUSKILL(1)
============

:Author:
	Michael Altfield (michael@michaelaltfield.net) and
	The BusKill Team (https://buskill.in/contact)

..
	=====================================
 	buskill 1 "2022" "Laptop Kill Cord"
	=====================================
	
	:Author: BusKill Team (https://buskill.in/contact/)
	:Date:   2022-12-09
	:Copyright: BusKill Team
	:Version: 0.7.0
	:Manual section: 1
	:Manual group: text processing
	
	.. TODO: authors and author with name <email>

	-------------------------------------------------------------------------
	Lock or shutdown if your device is stolen (for use with laptop kill cord)
	-------------------------------------------------------------------------

NAME
====

buskill - Lock or shutdown if your device is stolen (for use with laptop kill cord)

SYNOPSIS
========

buskill [options]

DESCRIPTION
===========

buskill is a cross-platform CLI and GUI app that can lock or shutdown your computer when a USB hotplug removal event occurs.

It's designed to work with the BusKill laptop kill cord, which is a hardware dead man switch that tethers a user to their computer via a USB cable with an integrated magnetic breakaway. If the cable is disconnected (eg by a snatch-and-run thief stealing the user's machine), then this software can trigger the computer to lock or shutdown -- thus protecting encrypted files (eg bitcoin private keys) or current login sessions (eg online banking) from theft.

OPTIONS
=======

**-h**, **--help**
: Show this help message and exit.

**--version**
: Print version and exit.

**--list-triggers**
: List all available triggers.

**-v**, **--verbose**
: Increase output verbosity.

**-t** , **--trigger**
: Choose trigger to execute. See --list-triggers for all possible values.

**-T**, **--run-trigger**
: Immediately execute the trigger on start.

**-a**, **--arm**
: Arms BusKill.

EXAMPLES
========

**buskill --list-triggers**
: Display all possible triggers, then exits.

**buskill --trigger lock-screen --arm**
: Arm the buskill app with the 'lock-screen' trigger so that a USB hotplug removal event will lock the device's screen

**buskill --trigger soft-shutdown --arm**
: Arm the buskill app with the 'soft-shutdown' trigger so that a USB hotplug removal event will cause the device to shutdown

SEE ALSO
========

This manpage is limited in scope. The BusKill project's main documentation (complete with images and videos) is available at `docs.buskill.in <https://docs.buskill.in>`__

* `Full Documentation <https://docs.buskill.in>`__
* `Official BusKill Project Website <https://buskill.in>`__
