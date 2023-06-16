#!/usr/bin/env python3
"""
::

  File:    buskill_cli.py
  Authors: Michael Altfield <michael@buskill.in>
  Created: 2020-06-23
  Updated: 2023-06-14
  Version: 0.3

This is the code to handle the BusKill app via CLI

For more info, see: https://buskill.in/
"""

################################################################################
#                                   IMPORTS                                    #
################################################################################

import packages.buskill
from buskill_version import BUSKILL_VERSION

import argparse, sys, platform, time

import logging
logger = logging.getLogger( __name__ )

################################################################################
#                                  SETTINGS                                    #
################################################################################

# n/a

################################################################################
#                                 FUNCTIONS                                    #
################################################################################

# blocking function that waits for the usb_handler to return a trigger event
def trigger_wait():

	# listen for the trigger event from the child process
	while True:

		result = bk.check_usb_handler(None)
		if result != None:
			break

		time.sleep(0.01)

	# wait until the asynchronous child process (that executes our
	# trigger) exits
	bk.usb_handler.join()

def BusKillCLI( buskill_object ):

	####################
	# HANDLE ARGUMENTS #
	####################

	global bk
	bk = buskill_object

	# we use ArgmentParser to handle the user's command-line arguents
	parser = argparse.ArgumentParser(
	 prog = "buskill",
	 description  = 'App for arming and configuring BusKill. For help, see https://docs.buskill.in'
	)

	parser.add_argument(
	 "--version",
	 help="print version and exit.",
	 action="store_true"
	)

	parser.add_argument(
	 "--list-triggers",
	 help="List all available triggers.",
	 action="store_true"
	)

	parser.add_argument(
	 "-v", "--verbose",
	 help="increase output verbosity",
	 action="store_true"
	)

	parser.add_argument(
	 "-t", "--trigger",
	 help="Choose trigger to execute. See --list-triggers for all possible values.",
	 metavar='',
	 choices=['l','lock-screen','s','soft-shutdown'],
	)

	parser.add_argument(
	 "-T", "--run-trigger",
	 help="Immediately execute the trigger on start",
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

	# standardize trigger name
	if args.trigger == 'l': args.trigger = 'lock-screen'
	if args.trigger == 's': args.trigger = 'soft-shutdown'

	#############
	# MAIN BODY #
	#############

	if args.version:
		print( "BusKill " +str(BUSKILL_VERSION['VERSION']) )
		print( "Build from branch " +str(BUSKILL_VERSION['GITHUB_REF']) )
		print( "Build from commit " +str(BUSKILL_VERSION['GITHUB_SHA']) )
		print( "Commit timestamp " +str(BUSKILL_VERSION['SOURCE_DATE_EPOCH']) )
		sys.exit(0)

	#global bk
	#bk = packages.buskill.BusKill()

	# is the OS that we're running on supported?
	if not bk.is_platform_supported():
		# the current platform isn't supported; show critical error window

		msg = bk.ERR_PLATFORM_NOT_SUPPORTED
		print( msg ); logger.error( msg )
		sys.exit(1)

	# did the user ask us to just list all available triggers?
	if args.list_triggers:
		print( "" )
		print( "Supported triggers include:" )
		for trigger in bk.SUPPORTED_TRIGGERS:
			print( "\t" +str(trigger))
		sys.exit(1)

	# did the user ask us to do a software upgrade?
	if args.upgrade:

		# check to see if this version has already been upgraded
		if bk.UPGRADED_TO:
			new_version_exe = bk.UPGRADED_TO['EXE_PATH']
			msg = "INFO: A newer upgrade has already been installed. Thew new executable is '" +str(new_version_exe)+ "'"
			print( msg ); logger.error( msg )
			sys.exit(1)

		try:
			new_version_exe = bk.upgrade()
		except RuntimeWarning as e:
			msg = "ERROR: Unable to upgrade buskill\n\t" +str(e)
			print( msg ); logger.error( msg )
			sys.exit(1)

		print( "Upgrade complete. New executable is '" +str(new_version_exe)+ "'" )

		sys.exit(0)

	# did the user say that we should execute the trigger immediately on startup?
	if args.run_trigger:
		try:
			bk.set_trigger( args.trigger )
			confirm = input("Are you sure you want to execute the '" +str(bk.get_trigger())+ "' trigger RIGHT NOW? [Y/N] ")

			# newline after input for cleaner output
			print()

			if confirm.upper() in ["Y", "YES"]:
				bk.simulate_hotplug_removal()

				trigger_wait()

			else:
				msg = "INFO: User chose not to execute trigger now. Exiting."
				print( msg ); logger.info( msg )
				bk.close()
				sys.exit(0)
		except RuntimeWarning as e:
			msg = "ERROR: Unable execute trigger\n\t" +str(e)
			print( msg ); logger.error( msg )
			bk.close()
			sys.exit(1)

		bk.close()
		sys.exit(0)

	# attempt to set the trigger
	try:
		if args.trigger != None:
			bk.set_trigger( args.trigger )
	except RuntimeWarning as e:
		msg = "ERROR: Unable to set the trigger to '" +str(args.trigger)+ "'\n\t" +str(e)
		print( msg ); logger.error( msg )
		sys.exit(1)

	if args.arm:
		bk.toggle()
		trigger_wait()

	else:
		msg = "Nothing to do."
		print( msg ); logger.warning( msg )

	return 0
