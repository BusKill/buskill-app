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
	...
	usage: buskill [-h] [--version] [--list-triggers] [-v] [-t] [-T] [-a] [-U]
	
	App for arming and configuring BusKill. For help, see https://docs.buskill.in
	
	optional arguments:
	  -h, --help         show this help message and exit
	  --version          print version and exit.
	  --list-triggers    List all available triggers.
	  -v, --verbose      increase output verbosity
	  -t , --trigger     Choose trigger to execute. See --list-triggers for all
	                     possible values.
	  -T, --run-trigger  Immediately execute the trigger on start
	  -a, --arm          Arms BusKill
	  -U, --upgrade      Download & upgrade latest version of BusKill
	user@disp2781:~/Downloads/dist$ 

Arming
------

To arm BusKill, execute it with the ``-a`` or ``--arm`` argument

::

	user@disp2781:~/Downloads/dist$ ./buskill.AppImage --arm
	...
	INFO: BusKill is armed. Listening for removal event.
	INFO: To disarm the CLI, exit with ^C or close this terminal
	user@disp2781:~/Downloads/dist$ 

Trigger Selector
^^^^^^^^^^^^^^^^

You can use ``-t`` or ``--trigger`` to specify which trigger you would like the BusKill app to execute when your BusKill cable is disconnected. For example, to arm BusKill such that it will shutdown your computer when the BusKill cable is removed, choose the ``soft-shutdown`` trigger

::

	user@disp2781:~/Downloads/dist$ ./buskill.AppImage --arm --trigger soft-shutdown
	...
	INFO: BusKill 'trigger' set to 'soft-shutdown'
	INFO: BusKill is armed. Listening for removal event.
	INFO: To disarm the CLI, exit with ^C or close this terminal

You can also list all available triggers with ``--list-triggers``

::

	user@disp2781:~/Downloads/dist$ ./buskill.AppImage --list-triggers
	...
	Supported triggers include:
		lock-screen
		soft-shutdown
	user@disp2781:~/Downloads/dist$ 

.. note::

	Due to a limitation in the Windows API, executables cannot be switched between ``CONSOLE`` and ``WINDOWS`` at runtime. This effectively means that ``buskill.exe`` *can* be executed from the CLI, but it won't be interactive. For more info, see:


	 * https://github.com/BusKill/buskill-app/issues/21

	As a simple workaround to launch the BusKill app in CLI mode, simply append ``| more`` to the command. For example, to arm the BusKill app from the CLI in the Windows Command Prompt:

	::
	
		C:\Users\user\Desktop\buskill-Windows\buskill>buskill.exe --arm | more

Disarming
---------

To disarm BusKill, simply send ``SIGTERM`` by typing ``ctrl+c`` or closing the terminal
