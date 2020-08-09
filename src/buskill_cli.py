#!/usr/bin/env python3.7
"""
::

  File:    buskill_cli.py
  Authors: Michael Altfield <michael@buskill.in>
  Created: 2020-06-23
  Updated: 2020-06-23
  Version: 0.1

This is the code to handle the BusKill app via CLI

For more info, see: https://buskill.in/
"""

################################################################################
#                                   IMPORTS                                    #
################################################################################

import buskill
import argparse, sys, platform

import logging
logger = logging.getLogger( __name__ )

################################################################################
#                                  SETTINGS                                    #
################################################################################

# n/a

################################################################################
#                                 FUNCTIONS                                    #
################################################################################

def BusKillCLI():

	####################
	# HANDLE ARGUMENTS #
	####################

	# we use ArgmentParser to handle the user's command-line arguents
	parser = argparse.ArgumentParser(
	 prog = "buskill",
	 description  = 'App for arming and configuring BusKill.'
	)

	parser.add_argument(
	 "-v", "--verbose",
	 help="increase output verbosity",
	 action="store_true"
	)

	parser.add_argument(
	 "-a", "--arm",
	 help="Arms BusKill",
	 action="store_true"
	)

	parser.add_argument(
	 "-U", "--upgrade",
	 help="Download & upgrade latest version of BusKill",
	 action="store_true"
	)

	# process command-line arguments
	args = parser.parse_args()

	#############
	# MAIN BODY #
	#############

	buskill.init()

	# is the OS that we're running on supported?
	if not buskill.isPlatformSupported():
		# the current platform isn't supported; show critical error window

		msg = buskill.ERR_PLATFORM_NOT_SUPPORTED
		print( msg ); logging.error( msg )
		sys.exit(1)

	if args.upgrade:
		buskill.upgrade()
		sys.exit(0)

	if args.arm:
		buskill.toggle()

	else:
		msg = "Nothing to do."
		print( msg ); logging.warning( msg )

	return 0
