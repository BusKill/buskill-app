.. _build_app:

Building buskill-app
====================

This section documents how to build the BusKill App.

.. note::

	Our build scripts are designed to be run on GitHub's shared runners -- disposable cloud instances. Therefore, our build scripts may make system-wide package changes and they may not cleanup at the end of their execution.

	We recommend that you execute these on a fresh disposable VM and take a snapshot before proceeding.

Linux
-----

Our build script is executed on GitHub's shared runners, which use Ubuntu. For better reproducibility, the build script itself is executed inside a wrapper script that installs and executes the build script in a debian docker container. For more information, see:

#. The `list of Ubuntu versions in GitHub's documentation <https://docs.github.com/en/actions/reference/virtual-environments-for-github-hosted-runners#supported-runners-and-hardware-resources>`_
#. Our `build logs <https://github.com/BusKill/buskill-app/actions?query=workflow%3Abuild>`_

::

	sudo su -
	sudo apt-get install git
	git clone https://github.com/BusKill/buskill-app.git
	cd buskill-app/
	build/linux/debianWrapper.sh 

.. note::

	When first setting up your build environment, it may be helpful to reference our `GitHub build workflow for Linux <https://github.com/BusKill/buskill-app/blob/master/.github/workflows/build.yml#L12-L22>`_.

After you've successfully built the app once, you can iterate more quickly by using the python binary used to build the AppImage to execute the ``src/main.py`` script directly. Call it with no arguments to execute it in GUI mode. If you add arguments, it will execute in CLI mode. For example

::

	user@buskill:~/sandbox/buskill-app$ /tmp/kivy_appdir/opt/python*/bin/python* src/main.py --help
	buskill version {'VERSION': '', 'GITHUB_REF': '', 'GITHUB_SHA': '', 'SOURCE_DATE_EPOCH': ''}
	usage: buskill [-h] [--version] [-v] [-a] [-l] [-U]
	
	App for arming and configuring BusKill. For help, see https://docs.buskill.in
	
	optional arguments:
  	-h, --help           show this help message and exit
  	--version            print version and exit.
  	-v, --verbose        increase output verbosity
  	-a, --arm            Arms BusKill
  	-l, --list-triggers  List triggers and exit
  	-U, --upgrade        Download & upgrade latest version of BusKill
	user@buskill:~/sandbox/buskill-app$ 

Windows
-------

Our build script is executed on GitHub's shared runners. For more information on the specific version of Windows you should use for best results, see:

#. The `list of Windows versions in GitHub's documentation <https://docs.github.com/en/actions/reference/virtual-environments-for-github-hosted-runners#supported-runners-and-hardware-resources>`_
#. Our `build logs <https://github.com/BusKill/buskill-app/actions?query=workflow%3Abuild>`_

::

	git clone https://github.com/BusKill/buskill-app.git
	cd buskill-app/
	build/windows/buildExe.ps1

.. note::

	When first setting up your build environment, it may be helpful to reference our `GitHub build workflow for Windows <https://github.com/BusKill/buskill-app/blob/master/.github/workflows/build.yml#L68-L73>`_.

MacOS
-----

Our build script is executed on GitHub's shared runners. For more information on the specific version of MacOS you should use for best results, see:

#. The `list of MacOS versions in GitHub's documentation <https://docs.github.com/en/actions/reference/virtual-environments-for-github-hosted-runners#supported-runners-and-hardware-resources>`_
#. Our `build logs <https://github.com/BusKill/buskill-app/actions?query=workflow%3Abuild>`_

::

	sudo su -
	git clone https://github.com/BusKill/buskill-app.git
	cd buskill-app/
	build/mac/buildDmg.sh	

.. note::

	When first setting up your build environment, it may be helpful to reference our `GitHub build workflow for MacOS <https://github.com/BusKill/buskill-app/blob/master/.github/workflows/build.yml#L118-L127>`_.
