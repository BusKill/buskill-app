#!/usr/bin/env python3.7
#import pdb;pdb.set_trace()
"""
::

  File:    main.py
  Authors: Michael Altfield <michael@buskill.in>
  Created: 2020-06-23
  Updated: 2020-06-23
  Version: 0.1

This is the main wrapper script for launching the BusKill app.

It has no functions and simply sets-up some essential requirements based on the platform, sets-up logging, and then either launches the CLI (``buskill_cli.py``) or the GUI (``buskill_gui.py``).

For more info, see: https://buskill.in/

"""

# this is needed for supporting Windows 10 with OpenGL < v2.0
# Example: VirtualBox w/ OpenGL v1.1
import platform, os
CURRENT_PLATFORM = platform.system().upper()
if CURRENT_PLATFORM.startswith( 'WIN' ):
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

################################################################################
#                                   IMPORTS                                    #
################################################################################

import argparse, logging, sys, multiprocessing, tempfile

################################################################################
#                                  SETTINGS                                    #
################################################################################

#BUSKILL_VERSION = '0.1'
from buskill_version import BUSKILL_VERSION

################################################################################
#                                  MAIN BODY                                   #
################################################################################

#################
# SETUP LOGGING #
#################

# TODO: disable logging by default; enable it with an argument
# TODO: be able to override the path to the log file with an env var or argument value; make these just the defaults
log_file_path = os.path.join( tempfile.gettempdir(), 'buskill.log' )

logging.basicConfig(
 filename = log_file_path,
 filemode = 'a',
 format = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
 datefmt = '%H:%M:%S',
 level = logging.DEBUG
)
logging.debug("===============================================================================")
logging.info( "INFO: Writing to log file '" +str(log_file_path)+ "'" )
logging.debug( 'BUSKILL_VERSION|' +str(BUSKILL_VERSION)+ '|' )
logging.debug( 'os.environ|' +str(os.environ)+ '|' )
logging.debug( 'sys.argv|' +str(sys.argv)+ '|' )
logging.debug( 'sys.builtin_modules_names|' +str(sys.builtin_module_names)+ '|' )
logging.debug( 'sys.executable|' +str(sys.executable)+ '|' )
logging.debug( 'sys.path|' +str(sys.path)+ '|' )
logging.debug( 'sys.platform|' +str(sys.platform)+ '|' )
logging.debug( 'sys.prefix|' +str(sys.prefix)+ '|' )
logging.debug( 'sys.version|' +str(sys.version)+ '|' )
logging.debug( 'sys.api_version|' +str(sys.api_version)+ '|' )
logging.debug( 'sys.version_info|' +str(sys.version_info)+ '|' )

if __name__ == '__main__':

	CURRENT_PLATFORM = platform.system().upper()

	# fix windows "error: unrecognized arguments: --multiprocessing-fork"
	# * kttps://stackoverflow.com/questions/46335842/python-multiprocessing-throws-error-with-argparse-and-pyinstaller
	multiprocessing.freeze_support()

	# fix macos error "The process has forked and you cannot use this CoreFoundation functionality safely. You MUST exec()."
	if CURRENT_PLATFORM.startswith( 'DARWIN' ):
		multiprocessing.set_start_method('spawn')

	msg = "buskill version " +str(BUSKILL_VERSION)
	print( msg ); logging.info( msg )

	# did we get any command-line arguments?
	if len(sys.argv) < 2:
		# we were given 0 command line arguments; just launch the GUI

		print( "No command-line arguments detected. Launching GUI" )
		print( "Hint: execute `buskill --help` for command-line usage" )

		from buskill_gui import BusKillApp
		BusKillApp().run()

	else:
		# the user passed-in arguments; give 'em the cli

		from buskill_cli import *
		ret = BusKillCLI()

		sys.exit( ret )

