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

import platform

import logging
logger = logging.getLogger( __name__ )

def init():
	global buskill_is_armed
	buskill_is_armed = False

	global ERR_PLATFORM_NOT_SUPPORTED
	ERR_PLATFORM_NOT_SUPPORTED = 'ERROR: Your platform (' +str(platform.system())+ ') is not supported. If you believe this is an error, please file a bug report:\n\nhttps://github.com/BusKill/buskill-app/issues'

	global CURRENT_PLATFORM
	CURRENT_PLATFORM = platform.system().upper()

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

	if isArmed():

		if CURRENT_PLATFORM.startswith( 'LINUX' ):
			disarmLin()
		if CURRENT_PLATFORM.startswith( 'WINDOWS' ):
			disarmWin()
		if CURRENT_PLATFORM.startswith( 'DARWIN' ):
			disarmMac()

		buskill_is_armed = False

	else:

		if CURRENT_PLATFORM.startswith( 'LINUX' ):
			armLin()
		if CURRENT_PLATFORM.startswith( 'WINDOWS' ):
			armWin()
		if CURRENT_PLATFORM.startswith( 'DARWIN' ):
			armMac()

		buskill_is_armed = True

def armLin():
	msg = "placeholder for arming buskill on linux"
	print( msg ); logger.info( msg )

def armWin():
	msg = "placeholder for arming buskill on windows"
	print( msg ); logger.info( msg )

def armMac():
	msg = "placeholder for arming buskill on a mac"
	print( msg ); logger.info( msg )

def disarmLin():
	msg = "placeholder for disarming buskill on linux"
	print( msg ); logger.info( msg )

def disarmWin():
	msg = "placeholder for disarming buskill on windows"
	print( msg ); logger.info( msg )

def disarmMac():
	msg = "placeholder for disarming buskill on a mac"
	print( msg ); logger.info( msg )

