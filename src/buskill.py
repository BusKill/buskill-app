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
		if platform.system() == 'Mac':
			disarmMac()

		buskill_is_armed = False

	else:

		if platform.system() == 'Linux':
			armLin()
		if platform.system() == 'Windows':
			armWin()
		if platform.system() == 'Mac':
			armMac()

		buskill_is_armed = True

def armMac():
	print( "placeholder for arming buskill on a mac" )

def armWin():
	print( "placeholder for arming buskill on windows" )

def armLin():
	print( "placeholder for arming buskill on linux" )

def disarmMac():
	print( "placeholder for disarming buskill on a mac" )

def disarmWin():
	print( "placeholder for disarming buskill on windows" )

def disarmLin():
	print( "placeholder for disarming buskill on linux" )
