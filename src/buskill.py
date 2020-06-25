#!/usr/bin/env python3.7
################################################################################
# File:    buskill.py
# Purpose: This is the heart of the buskill app, shared by both the cli and gui
#          For more info, see: https://buskill.in/
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-06-23
# Updated: 2020-06-23
# Version: 0.1
################################################################################

################################################################################
#                                   IMPORTS                                    #
################################################################################

import platform, usb1, multiprocessing, subprocess

import logging
logger = logging.getLogger( __name__ )

################################################################################
#                                  SETTINGS                                    #
################################################################################

# n/a

################################################################################
#                                  FUNCTIONS                                   #
################################################################################

def init():

	global buskill_is_armed
	buskill_is_armed = False

	global usb_handler

	global ERR_PLATFORM_NOT_SUPPORTED
	ERR_PLATFORM_NOT_SUPPORTED = 'ERROR: Your platform (' +str(platform.system())+ ') is not supported. If you believe this is an error, please file a bug report:\n\nhttps://github.com/BusKill/buskill-app/issues'

	global CURRENT_PLATFORM
	CURRENT_PLATFORM = platform.system().upper()

	global arm_fun
	global disarm_fun
	global trigger_fun
	if CURRENT_PLATFORM.startswith( 'LINUX' ):
		arm_fun = armLin
		disarm_fun = disarmLin
		trigger_fun = triggerLin

	if CURRENT_PLATFORM.startswith( 'WINDOWS' ):
		arm_fun = armWin
		disarm_fun = disarmWin
		trigger_fun = triggerWin

	if CURRENT_PLATFORM.startswith( 'DARWIN' ):
		arm_fun = armMac
		disarm_fun = disarmMac
		trigger_fun = triggerMac

# this is called when the GUI is closed 
def close():

	# if we don't kill this child process on kill, the UI will freeze
	usb_handler.terminate()

def isPlatformSupported():

	if CURRENT_PLATFORM.startswith( 'LINUX' ) \
	 or CURRENT_PLATFORM.startswith( 'WINDOWS' ) \
	 or CURRENT_PLATFORM.startswith( 'DARWIN' ):
		return True
	else:
		return False

def isArmed():
	return buskill_is_armed

def toggle():

	global buskill_is_armed
	global usb_handler

	if isArmed():
		msg = "DEBUG: attempting to disarm BusKill"
		print( msg ); logger.debug( msg )

		msg = "INFO: disarming BusKill (ignore the traceback below caused by killing the child process abruptly)"
		print( msg ); logger.info( msg )

		# TODO: maybe move this to diarmLin() if it doesn't work for Win/Mac
		# terminate our process that's looping & listening for usb events
		usb_handler.terminate()
		usb_handler.join()

		buskill_is_armed = False
		msg = "INFO: BusKill is disarmed."
		print( msg ); logger.info( msg )

	else:
		msg = "DEBUG: attempting to arm BusKill"
		print( msg ); logger.debug( msg )

		# launch an asynchronous child process that'll loop and listen for
		# usb events
		usb_handler = multiprocessing.Process(
		 target = arm_fun
		)
		usb_handler.start()

		buskill_is_armed = True

def trigger( *argv ):

	(context, device, event) = argv

	msg = "DEBUG: called trigger()"
	print( msg ); logger.debug( msg )

	# is this from a usb device being inserted or removed? 
	if event == usb1.HOTPLUG_EVENT_DEVICE_LEFT:
		# this is a usb removal event

		trigger_fun( *argv )

####################
# ARMING FUNCTIONS #
####################

def armLin():

	global usb_handler

	with usb1.USBContext() as context:

		if not context.hasCapability(usb1.CAP_HAS_HOTPLUG):
			msg = 'ERROR: Hotplug support is missing'
			print( msg ); logger.error( msg )
			return msg

		opaque = context.hotplugRegisterCallback( trigger )
		msg = "INFO: BusKill is armed. Listening for removal event.\n"
		msg+= "INFO: To disarm the CLI, exit with ^C or close this terminal"
		print( msg ); logger.info( msg )

		try:
			while True:
				# this call is blocking (with a default timeout of 60 seconds)
				# afaik there's no way to tell USBContext.handleEvents() to exit
				# safely, so instead we just make the whole call to this arming
				# function in a new child process and kill it on disarm with
				# terminate( )this approach isn't very nice and it dumps a
				# traceback to output, but it *does* immediately disarm without
				# having wait for the timeout..
				context.handleEvents()

		except (KeyboardInterrupt, SystemExit):
			print('Exiting')

	return 0

def armWin():
	msg = "placeholder for arming buskill on windows"
	print( msg ); logger.info( msg )

def armMac():
	msg = "placeholder for arming buskill on a mac"
	print( msg ); logger.info( msg )

#######################
# DISARMING FUNCTIONS #
#######################

def disarmLin():
	msg = "placeholder for disarming buskill on linux"
	print( msg ); logger.info( msg )

def disarmWin():
	msg = "placeholder for disarming buskill on windows"
	print( msg ); logger.info( msg )

def disarmMac():
	msg = "placeholder for disarming buskill on a mac"
	print( msg ); logger.info( msg )

#####################
# TRIGGER FUNCTIONS #
#####################

# TODO: add other triggers besides lockscreens

def triggerLin( context, device, event ):
	msg = "DEBUG: BusKill lockscreen trigger executing now"
	print( msg ); logger.debug( msg )

	try:
		subprocess.run( ['xdg-screensaver', 'lock'] )
		subprocess.run( ['xscreensaver', '-lock'] )
	except FileNotFoundError as e:
		pass

def triggerWin():
	msg = "placeholder for triggering buskill on windows"
	print( msg ); logger.info( msg )

def triggerMac():
	msg = "placeholder for triggering buskill on a mac"
	print( msg ); logger.info( msg )

