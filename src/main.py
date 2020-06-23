#!/usr/bin/env python3.7
################################################################################
# File:    main.py
# Purpose: This is the main wrapper script for launching the buskill app
#          For more info, see: https://buskill.in/
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-06-23
# Updated: 2020-06-23
# Version: 0.1
################################################################################

# this is needed for supporting Windows 10 with OpenGL < v2.0
# Example: VirtualBox w/ OpenGL v1.1
import platform, os
if platform.system() == 'Windows':
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

################################################################################
#                                   IMPORTS                                    #
################################################################################

import argparse

################################################################################
#                                  SETTINGS                                    #
################################################################################

BUSKILL_VERSION = '0.1'

################################################################################
#                                  MAIN BODY                                   #
################################################################################

if __name__ == '__main__':

	print( "buskill-app version " +str(BUSKILL_VERSION) )

	# we use ArgmentParser to handle the user's command-line arguents
	parser = argparse.ArgumentParser(
	 description  = 'App for arming and configuring BusKill. Use --help for more info.'
	)

	# process command-line arguments
	args = parser.parse_args()

	# did we get any command-line arguments?
	if args == argparse.Namespace():
		# we were given 0 command line arguments; just launch the GUI

		print( "No command-line arguments detected. Launching GUI" )
		print( "Hint: execute with --help for command-line usage" )

		import gui
		BusKill().run()

