#!/usr/bin/env python3.7
"""
::

  File:    packages/buskill/root_child_mac.py
  Authors: Michael Altfield <michael@buskill.in>
  Created: 2022-10-15
  Updated: 2022-10-15
  Version: 0.1

This is a very small python script that is intended to be run with root privileges on MacOS platforms. It should be as small and paranoid as possible, and only contain logic that cannot run as the normal user due to insufficient permissions (eg shutting down the machine)

For more info, see: https://buskill.in/
"""

################################################################################
#                                   IMPORTS                                    #
################################################################################

import os, re, sys, subprocess

################################################################################
#                                  SETTINGS                                    #
################################################################################

################################################################################
#                                  FUNCTIONS                                   #
################################################################################

# this function will gently shutdown a MacOS machine
def trigger_softshutdown_mac(self):
	msg = "DEBUG: BusKill soft-shutdown trigger executing now"
	#print( msg ); logger.debug( msg )
	log.write(msg); log.flush()

	# first we try to shutdown with `shutdown`
	trigger_softshutdown_mac_shutdown()

# shutdown the computer with the `shutdown` command
def trigger_softshutdown_mac_shutdown():

	try:
		# first try to shutdown with the `shutdown` command
		msg = "INFO: Attempting to execute `shutdown -h now"
		#print( msg ); logger.debug( msg )
		log.write(msg); log.flush()

		os.setuid(0)
		with open("/Users/administrator/buskill_root.out", "a") as f:
			f.write("I am root!\n")
			log.write( "I am root!\n" )

		# TODO: uncomment this to actually make it reboot
#		result = subprocess.run(
		# TODO: swap 'reboot' for actual 'shutdown' command
#		 #[ 'shutdown', '-h', 'now' ],
#		result = subprocess.run(
#		 [ 'reboot' ],
#		 capture_output=True,
#		 text=True
#		)
#
#		msg = "DEBUG: subprocess returncode|" +str(result.returncode)+ "|"
#		print( msg ); logger.debug( msg )
#
#		msg = "DEBUG: subprocess stdout|" +str(result.stdout)+ "|"
#		print( msg ); logger.debug( msg )
#
#		msg = "DEBUG: subprocess stderr|" +str(result.stderr)+ "|"
#		print( msg ); logger.debug( msg )
#
#		if result.returncode != 0:
#			# that didn't work; log it and try fallback
#			msg = "WARNING: Failed to execute `shutdown -h now`!"
#			print( msg ); logger.warning( msg )
#
#		trigger_softshutdown_mac_halt()

	except Exception as e:
		# that didn't work; log it and try fallback
		msg = "WARNING: Failed to execute `shutdown -h now`!"
		#print( msg ); logger.warning( msg )
		log.write(msg); log.flush()

		trigger_softshutdown_mac_halt()

# shutdown the computer with the `halt` command
def trigger_softshutdown_mac_halt():

	try:
		# try to shutdown with the `halt` command
		msg = "INFO: Attempting to execute `poweroff"
		#print( msg ); logger.debug( msg )
		log.write(msg); log.flush()

		os.setuid(0)
		with open("/Users/administrator/buskill_root.out", "a") as f:
			f.write("I am root!\n")
			log.write( "I am root!\n" )

		# TODO: uncomment this to actually make it actually halt
#		result = subprocess.run(
#		 #[ 'halt' ],
#		 [ 'reboot' ],
#		 capture_output=True,
#		 text=True
#		)
#
#		msg = "DEBUG: subprocess returncode|" +str(result.returncode)+ "|"
#		print( msg ); logger.debug( msg )
#
#		msg = "DEBUG: subprocess stdout|" +str(result.stdout)+ "|"
#		print( msg ); logger.debug( msg )
#
#		msg = "DEBUG: subprocess stderr|" +str(result.stderr)+ "|"
#		print( msg ); logger.debug( msg )
#
#		if result.returncode != 0:
#			# that didn't work; log it and give up :(
#			msg = "ERROR: Failed to execute `halt`! "
#			print( msg ); logger.error(msg)

	except Exception as e:
		# that didn't work; log it and give up :(
		msg = "ERROR: Failed to execute `halt`! " +str(e)
		#print( msg ); logger.error(msg)
		log.write(msg); log.flush()

################################################################################
#                                  MAIN BODY                                   #
################################################################################

# TODO: change manual logging to 'loggger' to the debug file (if possible)
log = open("/Users/maltfield/.buskill/root_child.log", "a")
log.write( "==============================================\n" )

# loop and listen for commands from the parent process
while True:

	# block until we recieve a command (ending with a newline) from stdin
	command = sys.stdin.buffer.readline().strip().decode('ascii')
	log.write( "INFO: Command received\n" ); log.flush()

	# check sanity of recieved command. Be very suspicious
	if not re.match( "^[A-Za-z_-]+$", command ):
		msg = "ERROR: Bad Command Ignored\n"

		log.write(str(msg)); log.flush()
		sys.stdout.buffer.write( msg.encode(encoding='ascii') )
		sys.stdout.flush()
		continue

	# what was the command they sent us?
	if command == "soft-shutdown":
		# they want us to shutdown the machine; do it!

		try:
			trigger_softshutdown_mac()
			msg = "SUCCESS: I am root!\n"

		except Exception as e:
			msg = "ERROR: I am not root :'(\n"

	else:   
		# I have no idea what they want; tell them we ignored the request
		msg = "WARNING: Unknown Command Ignored\n"

	#print( msg ); logger.debug( msg )
	log.write(msg); log.flush()
	sys.stdout.buffer.write( msg.encode(encoding='ascii') )
	sys.stdout.flush()

# TODO: See if it's possible to put this in a function that's registered as
#       a callback when the process is closing
log.close()
