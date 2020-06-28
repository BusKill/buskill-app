#!/usr/bin/env python3.7
################################################################################
# File:    buskill.py
# Purpose: This is the heart of the buskill app, shared by both the cli and gui
#          For more info, see: https://buskill.in/
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-06-23
# Updated: 2020-06-28
# Version: 0.1
################################################################################

################################################################################
#                                   IMPORTS                                    #
################################################################################

import platform, multiprocessing, subprocess

import logging
logger = logging.getLogger( __name__ )

# platform-specific modules
CURRENT_PLATFORM = platform.system().upper()
if CURRENT_PLATFORM.startswith( 'LINUX' ):
	import usb1

if CURRENT_PLATFORM.startswith( 'WIN' ):
	import win32api, win32con, win32gui
	from ctypes import *

if CURRENT_PLATFORM.startswith( 'DARWIN' ):
	import usb1

################################################################################
#                                  SETTINGS                                    #
################################################################################

#####################
# WINDOWS CONSTANTS #
#####################

if CURRENT_PLATFORM.startswith( 'WIN' ):

	# Device change events (WM_DEVICECHANGE wParam)
	DBT_DEVICEARRIVAL = 0x8000
	DBT_DEVICEQUERYREMOVE = 0x8001
	DBT_DEVICEQUERYREMOVEFAILED = 0x8002
	DBT_DEVICEMOVEPENDING = 0x8003
	DBT_DEVICEREMOVECOMPLETE = 0x8004
	DBT_DEVICETYPESSPECIFIC = 0x8005
	DBT_CONFIGCHANGED = 0x0018

	# type of device in DEV_BROADCAST_HDR
	DBT_DEVTYP_OEM = 0x00000000
	DBT_DEVTYP_DEVNODE = 0x00000001
	DBT_DEVTYP_VOLUME = 0x00000002
	DBT_DEVTYPE_PORT = 0x00000003
	DBT_DEVTYPE_NET = 0x00000004

	# media types in DBT_DEVTYP_VOLUME
	DBTF_MEDIA = 0x0001
	DBTF_NET = 0x0002

	WORD = c_ushort
	DWORD = c_ulong

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

	# platform-specific setup
	global arm_fun
	global disarm_fun
	global trigger_fun
	if CURRENT_PLATFORM.startswith( 'LINUX' ):
		arm_fun = armNix
		trigger_fun = triggerLin

	if CURRENT_PLATFORM.startswith( 'WIN' ):
		arm_fun = armWin
		trigger_fun = triggerWin

	if CURRENT_PLATFORM.startswith( 'DARWIN' ):
		arm_fun = armNix
		trigger_fun = triggerMac

# this is called when the GUI is closed 
def close():

	# if we don't kill this child process on kill, the UI will freeze
	usb_handler.terminate()

def isPlatformSupported():

	if CURRENT_PLATFORM.startswith( 'LINUX' ) \
	 or CURRENT_PLATFORM.startswith( 'WIN' ) \
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

		# disarm just means to terminate the child process in which the arm
		# function was spawned. this works on all platforms.
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

# this is a callback function that is registered to be called when a usb
# hotplug event occurs using libusb (linux & macos)
def hotplugCallbackNix( *argv ):

	(context, device, event) = argv

	msg = "DEBUG: called hotplugCallbackNix()"
	print( msg ); logger.debug( msg )

	msg = "context:|" +str(context)+ "|"
	print( msg ); logger.debug( msg )

	msg = "device:|" +str(device)+ "|"
	print( msg ); logger.debug( msg )

	msg = "event:|" +str(event)+ "|"
	print( msg ); logger.debug( msg )

	# is this from a usb device being inserted or removed? 
	if event == usb1.HOTPLUG_EVENT_DEVICE_LEFT:
		# this is a usb removal event

		trigger_fun()

############################
# WINDOWS HELPER FUNCTIONS #
############################

# The windows WM_DEVICECHANGE code below was adapted from the following sources:
# * http://timgolden.me.uk/python/win32_how_do_i/detect-device-insertion.html
# * https://stackoverflow.com/questions/38689090/detect-media-insertion-on-windows-in-python

if CURRENT_PLATFORM.startswith( 'WIN' ):

	class DEV_BROADCAST_HDR(Structure):
		_fields_ = [
		 ("dbch_size", DWORD),
		 ("dbch_devicetype", DWORD),
		 ("dbch_reserved", DWORD)
		]
	
	class DEV_BROADCAST_VOLUME(Structure):
		_fields_ = [
		 ("dbcv_size", DWORD),
		 ("dbcv_devicetype", DWORD),
		 ("dbcv_reserved", DWORD),
		 ("dbcv_unitmask", DWORD),
		 ("dbcv_flags", WORD)
		]
	
	def drive_from_mask(mask):
		n_drive = 0
		while 1:
			if (mask & (2 ** n_drive)):
				return n_drive
			else:
				n_drive += 1
	
	class Notification:
		def __init__(self):
			message_map = {
			 win32con.WM_DEVICECHANGE: self.hotplugCallbackWin
			}
	
			wc = win32gui.WNDCLASS()
			hinst = wc.hInstance = win32api.GetModuleHandle(None)
			wc.lpszClassName = "DeviceChangeDemo"
			wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
			wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
			wc.hbrBackground = win32con.COLOR_WINDOW
			wc.lpfnWndProc = message_map
			classAtom = win32gui.RegisterClass(wc)
			style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
			self.hwnd = win32gui.CreateWindow(
			 classAtom,
			 "Device Change Demo",
			 style,
			 0, 0,
			 win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
			 0, 0,
			 hinst, None
			)
	
		# this is a callback function that is registered to be called when a usb
		# hotplug event occurs in windows
		# WM_DEVICECHANGE:
		#  wParam - type of change: arrival, removal etc.
		#  lParam - what's changed?
		#    if it's a volume then...
		#  lParam - what's changed more exactly
		def hotplugCallbackWin(self, hwnd, message, wparam, lparam):
	
			dev_broadcast_hdr = DEV_BROADCAST_HDR.from_address(lparam)
	
			if wparam == DBT_DEVICEREMOVECOMPLETE:
	
				triggerWin()
	
				msg = "hwnd:|" +str(hwnd)+ "|"
				print( msg ); logger.debug( msg )

				msg = "message:|" +str(message)+ "|"
				print( msg ); logger.debug( msg )

				msg= "wparam:|" +str(wparam)+ "|"
				print( msg ); logger.debug( msg )

				msg = "lparam:|" +str(lparam)+ "|"
				print( msg ); logger.debug( msg )
	
				dev_broadcast_volume = DEV_BROADCAST_VOLUME.from_address(lparam)
				msg = "dev_broadcast_volume:|" +str(dev_broadcast_volume)+ "|"
				print( msg ); logger.debug( msg )

				drive_letter = drive_from_mask(dev_broadcast_volume.dbcv_unitmask)
				msg = "drive_letter:|" +str(drive_letter)+ "|"
				print( msg ); logger.debug( msg )

				msg = "ch( ord('A') + drive_letter):|" +str( chr(ord('A') + drive_letter) )+ '|'
				print( msg ); logger.debug( msg )
	
			return 1

####################
# ARMING FUNCTIONS #
####################

# this works for both linux and mac
def armNix():

	with usb1.USBContext() as context:

		if not context.hasCapability(usb1.CAP_HAS_HOTPLUG):
			msg = 'ERROR: Hotplug support is missing'
			print( msg ); logger.error( msg )
			return msg

		opaque = context.hotplugRegisterCallback( hotplugCallbackNix )
		msg = "INFO: BusKill is armed. Listening for removal event.\n"
		msg+= "INFO: To disarm the CLI, exit with ^C or close this terminal"
		print( msg ); logger.info( msg )

		try:
			while True:
				# this call is blocking (with a default timeout of 60 seconds)
				# afaik there's no way to tell USBContext.handleEvents() to exit
				# safely, so instead we just make the whole call to this arming
				# function in a new child process and kill it on disarm with
				# terminate() this approach isn't very nice and it dumps a
				# traceback to output, but it *does* immediately disarm without
				# having wait for the timeout..
				context.handleEvents()

		except (KeyboardInterrupt, SystemExit):
			print('Exiting')

	return 0

def armWin():

	w = Notification()
	win32gui.PumpMessages()
#####################
# TRIGGER FUNCTIONS #
#####################

# TODO: add other triggers besides lockscreens

def triggerLin():
	msg = "DEBUG: BusKill lockscreen trigger executing now"
	print( msg ); logger.debug( msg )

	try:
		subprocess.run( ['xdg-screensaver', 'lock'] )
		subprocess.run( ['xscreensaver', '-lock'] )
	except FileNotFoundError as e:
		pass

def triggerWin():
	msg = "DEBUG: BusKill lockscreen trigger executing now"
	print( msg ); logger.debug( msg )

	windll.user32.LockWorkStation()

def triggerMac():
	msg = "placeholder for triggering buskill on a mac"
	print( msg ); logger.info( msg )

	try:
		subprocess.run( ['pmset', 'displaysleepnow'] )
	except FileNotFoundError as e:
		subprocess.run( ['/System/Library/CoreServices/Menu Extras/user.menu/Contents/Resources/CGSession', '-suspend'] )
