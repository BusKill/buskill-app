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

import os, time, re, sys, subprocess

################################################################################
#                                  SETTINGS                                    #
################################################################################

################################################################################
#                                  FUNCTIONS                                   #
################################################################################

# shutdown the computer with the `shutdown` command
# TODO: fall-back to poweroff
def soft_shutdown():
        try:
                proc = subprocess.Popen(
						# TODO: switch this back to shutdown (from reboot)
                 #[ 'sudo', 'shutdown', '-h', 'now' ],
                 [ 'reboot' ],
                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
                )
        except Exception as e:
                print( "I am not root :'(" )


################################################################################
#                                  MAIN BODY                                   #
################################################################################

if __name__ == "__main__":

	# TODO: change manual logging to 'loggger' to the debug file (if possible)
	log = open("/Users/maltfield/.buskill/root_child.log", "a")
	log.write( "==============================================\n" )
	log.write( "attempting to write to root-only file\n" )

	# loop and listen for commands from the parent process
while True:

	# block until we recieve a command (ending with a newline) from stdin
	command = sys.stdin.buffer.readline().strip().decode('ascii')

	# check sanity of recieved command. Be very suspicious
	if not re.match( "^[A-Za-z_-]+$", command ):
		msg = "ERROR: Bad Command Ignored\n"

		log.write(); log.flush()
		sys.stdout.buffer.write( msg.encode(encoding='ascii') )
		sys.stdout.flush()
		continue

	# what was the command they sent us?
	if command == "soft-shutdown":
		# they want us to shutdown the machine; do it!

		try:
			soft_shutdown()
			msg = "SUCCESS: I am root!\n"

		except Exception as e:
			msg = "ERROR: I am not root :'(\n"

	else:   
		# I have no idea what they want; tell them we ignored the request
		msg = "WARNING: Unknown Command Ignored\n"

	log.write(); log.flush()
	sys.stdout.buffer.write( msg.encode(encoding='ascii') )
	sys.stdout.flush()

# TODO: See if it's possible to put this in a function that's registered as
#       a callback when the process is closing
log.close()
