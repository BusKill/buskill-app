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
  	-U, --upgrade        Download & upgrade latest version of BusKill
	user@buskill:~/sandbox/buskill-app$ 

Windows
-------

Our build script is executed on GitHub's shared runners. For more information on the specific version of Windows you should use for best results, see:

#. The `list of Windows versions in GitHub's documentation <https://docs.github.com/en/actions/reference/virtual-environments-for-github-hosted-runners#supported-runners-and-hardware-resources>`_
#. Our `build logs <https://github.com/BusKill/buskill-app/actions?query=workflow%3Abuild>`_

.. note::

	When first setting up your build environment, it may be helpful to reference our `GitHub build workflow for Windows <https://github.com/BusKill/buskill-app/blob/master/.github/workflows/build.yml#L68-L73>`_.

::

	git clone https://github.com/BusKill/buskill-app.git
	cd buskill-app/
	build/windows/buildExe.ps1

.. note::

	Run the ``build\windows\buildExe.ps1`` script from inside a powershell.

   If you get Permission Denied issues, open a new PowerShell as root (Open as Administrator), and enter the following commands

     Set-ExecutionPolicy Unrestricted
     Set-ExecutionPolicy -Scope CurrentUser Unrestricted

	And in general, we recommend using cygwin when building on Windows.

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

After you've successfully built the app once, you can iterate more quickly by using the python binary that was used to build the MacOS release with PyInstaller to execute the ``src/main.py`` script directly. Call it with no arguments to execute it in GUI mode. If you add arguments, it will execute in CLI mode. For example

::

	user@host buskill-app % bash
	
	The default interactive shell is now zsh.
	To update your account to use zsh, please run `chsh -s /bin/zsh`.
	For more details, please visit https://support.apple.com/kb/HT208050.
	bash-3.2$ 

	bash-3.2$ cd sandbox/buskill-app
	bash-3.2$ grep 'PYTHON_PATH=' build/mac/buildDmg.sh | head -n1
	PYTHON_PATH="`find /usr/local/Cellar/python* -type f -wholename *bin/python3* | sort -n | uniq | head -n1`"
	bash-3.2$ PYTHON_PATH="`find /usr/local/Cellar/python* -type f -wholename *bin/python3* | sort -n | uniq | head -n1`"
	bash-3.2$ 
	
	bash-3.2$ $PYTHON_PATH src/main.py --help
	===============================================================================
	INFO: Writing to log file '/var/folders/kx/2fp3kfgj4dj7rx9s5mlb52640000gp/T/buskill.log'
	buskill version {'VERSION': '', 'GITHUB_REF': '', 'GITHUB_SHA': '', 'SOURCE_DATE_EPOCH': ''}
	usb1.__version__:|1.8|
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
	bash-3.2$ 

And (also after you've already successfully built the app once), you can iterate faster yet still build the ``.app`` dir with compiled binaries by executing PyInstaller directly. For example.

::

	user@host ~ % bash
	
	The default interactive shell is now zsh.
	To update your account to use zsh, please run `chsh -s /bin/zsh`.
	For more details, please visit https://support.apple.com/kb/HT208050.
	bash-3.2$ cd sandbox/buskill-app/pyinstaller/
	bash-3.2$ 
	
	bash-3.2$ grep 'PYTHON_PATH=' ../build/mac/buildDmg.sh | head -n1
	PYTHON_PATH="`find /usr/local/Cellar/python* -type f -wholename *bin/python3* | sort -n | uniq | head -n1`"
	bash-3.2$ PYTHON_PATH="`find /usr/local/Cellar/python* -type f -wholename *bin/python3* | sort -n | uniq | head -n1`"
	bash-3.2$ 
	
	bash-3.2$ $PYTHON_PATH -m PyInstaller -y --clean --windowed buskill.spec
	...
	34250 INFO: Building BUNDLE BUNDLE-00.toc completed successfully.
	bash-3.2$ 
	
	bash-3.2$ dist/buskill-dev.app/Contents/MacOS/buskill --help
	===============================================================================
	INFO: Writing to log file '/var/folders/kx/2fp3kfgj4dj7rx9s5mlb52640000gp/T/buskill.log'
	buskill version {'VERSION': '', 'GITHUB_REF': '', 'GITHUB_SHA': '', 'SOURCE_DATE_EPOCH': ''}
	usb1.__version__:|1.8|
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
	bash-3.2$ 
