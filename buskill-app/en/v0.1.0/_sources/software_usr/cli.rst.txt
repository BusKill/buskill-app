.. _cli:

BusKill App: Command-Line Interface
=====================================

This page will describe how to use the BusKill app in CLI mode.

To control BusKill via the CLI, use the same executable with arguments (executing ``buskill`` without arguments opens it in GUI mode).

Help
----

You can print a list of allowable arguments by passing the ``buskill`` app ``-h`` or ``--help``

::

	user@disp2781:~/Downloads/dist$ ./buskill.AppImage --help
	buskill version {'GITHUB_REF': 'refs/heads/v0.1.0', 'GITHUB_SHA': '120db24f2334071404e238123b94e51cf5987dce', 'SOURCE_DATE_EPOCH': '1596189086'}
	usage: buskill [-h] [-v] [-a]
	
	App for arming and configuring BusKill.
	
	optional arguments:
	  -h, --help     show this help message and exit
	  -v, --verbose  increase output verbosity
	  -a, --arm      Arms BusKill
	user@disp2781:~/Downloads/dist$ 

Arming
------

To arm BusKill, execute it with the ``-a`` or ``--arm`` argument

::

	user@disp2781:~/Downloads/dist$ ./buskill.AppImage --arm
	buskill version {'GITHUB_REF': 'refs/heads/v0.1.0', 'GITHUB_SHA': '120db24f2334071404e238123b94e51cf5987dce', 'SOURCE_DATE_EPOCH': '1596189086'}
	DEBUG: attempting to arm BusKill
	INFO: BusKill is armed. Listening for removal event.
	INFO: To disarm the CLI, exit with ^C or close this terminal


Disarming
---------

To disarm BusKill, simply send ``SIGTERM`` by typing ``ctrl+c`` or closing the terminal
