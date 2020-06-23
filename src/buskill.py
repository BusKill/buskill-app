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

def isPlatformSupported():
	if platform.system() in [ 'Linux', 'Windows', 'Darwin' ]:
		return True
	else:
		return False

def isArmed():
	global buskill_is_armed
	return buskill_is_armed

def toggle():

	global buskill_is_armed

	if isArmed():

		if platform.system() == 'Linux':
			disarmLin()
		if platform.system() == 'Windows':
			disarmWin()
		if platform.system() == 'Darwin':
			disarmMac()

		buskill_is_armed = False

	else:

		if platform.system() == 'Linux':
			armLin()
		if platform.system() == 'Windows':
			armWin()
		if platform.system() == 'Darwin':
			armMac()

		buskill_is_armed = True

def armMac():
	msg = "placeholder for arming buskill on a mac"
	print( msg ); logger.info( msg )

def armWin():
	msg = "placeholder for arming buskill on windows"
	print( msg ); logger.info( msg )

def armLin():
	msg = "placeholder for arming buskill on linux"
	print( msg ); logger.info( msg )

def disarmMac():
	msg = "placeholder for disarming buskill on a mac"
	print( msg ); logger.info( msg )

def disarmWin():
	msg = "placeholder for disarming buskill on windows"
	print( msg ); logger.info( msg )

def disarmLin():
	msg = "placeholder for disarming buskill on linux"
	print( msg ); logger.info( msg )
