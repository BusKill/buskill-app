.. _depends:

Dependencies
============

This section documents the various software dependencies of the BusKill App.

Note that our releases are self-contained executables that already include these dependencies, so you do not need to install them on your machine to run the BusKill software. This documentation is for informational purposes only.

All Platforms
-------------

The following software is a dependency for the BusKill app on all our releases for all platforms.

#. `python <https://www.python.org>`_ (`PSF <https://docs.python.org/3/license.html>`_)
#. `GnuPG <https://www.gnupg.org/>`_ (`GPL-3+ <https://www.gnupg.org/faq/HACKING.html>`_)

We also depend on the following python modules

#. `gnupg <https://github.com/vsajip/python-gnupg>`_ (`BSD <https://github.com/vsajip/python-gnupg/blob/master/LICENSE.txt>`_)
#. `kivy <https://kivy.org/>`_ (`MIT <https://github.com/kivy/kivy/blob/master/LICENSE>`_)

We also use the following python modules, which are built-into python

#. argparse
#. logging
#. sys
#. multiprocessing
#. threading
#. subprocess
#. tempfile
#. platform
#. os
#. re
#. math
#. random
#. distutils
#. hashlib
#. webbrowser
#. textwrap
#. shutil
#. traceback
#. pickle
#. urllib
#. certifi
#. json
#. tarfile
#. zipfile

Linux
-----

The following software is a dependency for the BusKill app only in the Linux builds.

..
	#. TODO

We also depend on the following python modules

#. `libusb1 <https://github.com/vpelletier/python-libusb1>`_ (`LGPLv2+ <https://github.com/vpelletier/python-libusb1/blob/master/COPYING.LESSER>`_)

Windows
-------

The following software is a dependency for the BusKill app only in the Windows builds.

..
	#. TODO

	We also depend on the following python modules

	#. TODO

And we also use the following python modules, which are built-into python

#. ctypes
#. win32api
#. win32con
#. win32gui

MacOS
-----

The following software is a dependency for the BusKill app only in the MacOS builds.

#. `gettext <https://savannah.gnu.org/projects/gettext/>`_ (`GPL-3+ <https://git.savannah.gnu.org/gitweb/?p=gettext.git;a=blob_plain;f=COPYING;hb=HEAD>`_)

We also depend on the following python modules

#. `libusb1 <https://github.com/vpelletier/python-libusb1>`_ (`LGPLv2+ <https://github.com/vpelletier/python-libusb1/blob/master/COPYING.LESSER>`_)

And we also use the following python modules, which are built-into python

#. ctypes
