#!/usr/bin/env python3
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

import logging, re, sys, subprocess

################################################################################
#                                  SETTINGS                                    #
################################################################################

################################################################################
#                                  FUNCTIONS                                   #
################################################################################

# this function will gently shutdown a MacOS machine
def trigger_softshutdown_mac():
	msg = "BusKill soft-shutdown trigger executing now"
	logging.debug( msg )

	# first we try to shutdown with `shutdown`
	trigger_softshutdown_mac_shutdown()

# shutdown the computer with the `shutdown` command
def trigger_softshutdown_mac_shutdown():

	try:
		# first try to shutdown with the `shutdown` command
		msg = "Attempting to execute `shutdown -h now`"
		logging.info(msg)

		# TODO: swap 'reboot' for actual 'shutdown' command
		result = subprocess.run(
		 #[ 'reboot' ],
		 [ 'shutdown', '-h', 'now' ],
		 capture_output=True,
		 text=True
		)

		msg = "subprocess returncode|" +str(result.returncode)+ "|"
		logging.debug(msg)

		msg = "subprocess stdout|" +str(result.stdout)+ "|"
		logging.debug(msg)

		msg = "subprocess stderr|" +str(result.stderr)+ "|"
		logging.debug(msg)

		if result.returncode != 0:
			# that didn't work; log it and try fallback
			msg = "Failed to execute `shutdown -h now`!"
			logging.warning(msg)

		trigger_softshutdown_mac_halt()

	except Exception as e:
		# that didn't work; log it and try fallback
		msg = "Failed to execute `shutdown -h now`!"
		logging.warning(msg)

		trigger_softshutdown_mac_halt()

# shutdown the computer with the `halt` command
def trigger_softshutdown_mac_halt():

	try:
		# try to shutdown with the `halt` command
		msg = "Attempting to execute `halt"
		logging.info(msg)

		result = subprocess.run(
		 #[ 'reboot' ],
		 [ 'halt' ],
		 capture_output=True,
		 text=True
		)

		msg = "subprocess returncode|" +str(result.returncode)+ "|"
		logging.debug(msg)

		msg = "subprocess stdout|" +str(result.stdout)+ "|"
		logging.debug(msg)

		msg = "subprocess stderr|" +str(result.stderr)+ "|"
		logging.debug(msg)

		if result.returncode != 0:
			# that didn't work; log it and give up :(
			msg = "Failed to execute `halt`! "
			logging.error(msg)

	except Exception as e:
		# that didn't work; log it and give up :(
		msg = "Failed to execute `halt`! " +str(e)
		logging.error(msg)

################################################################################
#                                  MAIN BODY                                   #
################################################################################

####################
# HANDLE ARGUMENTS #
####################

# the first argument is the file path to where we write logs
log_file_path = sys.argv[1]

# check sanity of input. Be very suspicious
if not re.match( "^[A-Za-z0-9\-\_\./\ ]+$", log_file_path ):
	print( "First positional argument (log file path) is invalid. Exiting" )
	sys.exit(1)

#################
# SETUP LOGGING #
#################

logging.basicConfig(
 filename = log_file_path,
 filemode = 'a',
 format = '%(asctime)s,%(msecs)d root_child %(levelname)s %(message)s',
 datefmt = '%H:%M:%S',
 level = logging.DEBUG
)

msg = "==============================================================================="
logging.info(msg)
msg = "root_child_mac is writing to log file '" +str(log_file_path)+ "'"
logging.info(msg)

#############
# MAIN LOOP #
#############

# loop and listen for commands from the parent process
while True:

	msg = "Waiting for command"
	logging.info(msg)

	# block until we recieve a command (ending with a newline) from stdin
	command = sys.stdin.buffer.readline().strip().decode('ascii')
	msg = "Command received"
	logging.info(msg)

	# check sanity of recieved command. Be very suspicious
	if not re.match( "^[A-Za-z_-]+$", command ):
		msg = "Bad Command Ignored\n"

		logging.error(msg)
		sys.stdout.buffer.write( msg.encode(encoding='ascii') )
		sys.stdout.flush()
		continue

	# what was the command they sent us?
	if command == "soft-shutdown":
		# they want us to shutdown the machine; do it!
		msg = "Command is 'soft-shutdown'"
		logging.debug(msg)

		try:
			msg = "Attempting to call trigger_softshutdown_mac()"
			logging.debug(msg)

			trigger_softshutdown_mac()
			msg = "Finished executing 'soft-shutdown'\n"
			logging.info(msg)

		except Exception as e:
			msg = "Failed to execute trigger_softshutdown_mac()\n" +str(e)
			logging.error(msg)

	else:   
		# I have no idea what they want; tell them we ignored the request
		msg = "Unknown Command Ignored\n"
		logging.warning(msg)

	sys.stdout.buffer.write( msg.encode(encoding='ascii') )
	sys.stdout.flush()
