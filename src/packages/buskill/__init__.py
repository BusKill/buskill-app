#!/usr/bin/env python3.7
"""
::

  File:    buskill.py
  Authors: Michael Altfield <michael@buskill.in>
  Co-Auth: Steven Johnson <steven.j2019@protonmail.com>
  Created: 2020-06-23
  Updated: 2022-07-11
  Version: 0.4

This is the heart of the buskill app, shared by both the cli and gui

For more info, see: https://buskill.in/
"""

################################################################################
#                                   IMPORTS                                    #
################################################################################

import platform, multiprocessing, traceback, subprocess
import urllib.request, re, json, certifi, sys, os, math, shutil, tempfile, random, gnupg
import os.path
from buskill_version import BUSKILL_VERSION
from distutils.version import LooseVersion
from hashlib import sha256

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

# APP_DIR is the dir in which our buskill executable lives, which often
# is some dir on the USB drive itself or could be somewhere on the computer
global APP_DIR
APP_DIR = sys.path[0]

UPGRADE_MIRRORS = [
 'https://raw.githubusercontent.com/BusKill/buskill-app/master/updates/v1/meta.json',
 'https://gitlab.com/buskill/buskill-app/-/raw/master/updates/v1/meta.json',
 'https://repo.buskill.in/buskill-app/v1/meta.json',
 'https://repo.michaelaltfield.net/buskill-app/v1/meta.json',
]
random.shuffle(UPGRADE_MIRRORS)

RELEASE_KEY_FINGERPRINT = 'E0AFFF57DC00FBE0563587614AE21E1936CE786A'
RELEASE_KEY_SUB_FINGERPRINT = '798DC1101F3DEC428ADE124D68B8BCB0C5023905'

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
#                                   OBJECTS                                    #
################################################################################

##########################
# WINDOWS HELPER CLASSES #
##########################

if CURRENT_PLATFORM.startswith( 'WIN' ):

	# The windows WM_DEVICECHANGE code below was adapted from the following sources:
	# * http://timgolden.me.uk/python/win32_how_do_i/detect-device-insertion.html
	# * https://stackoverflow.com/questions/38689090/detect-media-insertion-on-windows-in-python

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

		def __init__( self, buskill ):

			self.bk = buskill

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
	
				self.bk.triggerWin()
	
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

class BusKill:

	def __init__(self):

		###############################
		# instantiate instance fields #
		###############################

		self.CURRENT_PLATFORM = None
		self.KERNEL_VERSION = None
		self.IS_PLATFORM_SUPPORTED = False
		self.OS_NAME_SHORT = None
		self.ERR_PLATFORM_NOT_SUPPORTED = None
		self.ARM_FUNCTION = None
		self.DISARM_FUNCTION = None
		self.TRIGGER_FUNCTION = None
		self.EXE_PATH = None
		self.EXE_DIR = None
		self.EXE_FILE = None
		self.APP_DIR = None
		self.APPS_DIR = None
		self.DATA_DIR = None
		self.CACHE_DIR = None
		self.GNUPGHOME = None
		self.UPGRADED_FROM = None
		self.UPGRADED_TO = None

		self.is_armed = None
		self.usb_handler = None
		self.upgrade_status_msg = None
		self.upgrade_result = None

		# documentation links
		if BUSKILL_VERSION['VERSION'] == '':
			ver = 'stable'
		else:
			ver = BUSKILL_VERSION['VERSION']
		self.url_website = "https://buskill.in"
		self.url_documentation = "https://docs.buskill.in"
		self.url_documentation_contribute = "https://docs.buskill.in/buskill-app/en/stable/contributing.html"
		self.url_documentation_bug_report = 'https://docs.buskill.in/buskill-app/en/' +str(ver)+ '/support.html'
		self.url_documentation_gui = 'https://docs.buskill.in/buskill-app/en/' +str(ver)+ '/software_usr/gui.html'

		self.CURRENT_PLATFORM = platform.system().upper()
		self.ERR_PLATFORM_NOT_SUPPORTED = 'ERROR: Your platform (' +str(platform.system())+ ') is not supported. If you believe this is an error, please file a bug report:\n\nhttps://github.com/BusKill/buskill-app/issues'

		# NOTE about instance fields used for storing path info relative to the
		#      buskill executable:
		#
		# 1. EXE_PATH = the absolute path to the executable for running BusKill,
		#               which is:
		#                 [a] the 'buskill-<version>.AppImage' file in Linux
		#                 [b] the 'buskill.exe' file in Windows
		#                 [c] the 'buskill' binary file in MacOS
		# 2. EXE_FILE = just the filename (basename) of the EXE_PATH
		# 3. EXE_DIR = the directory (dirname) where EXE_FILE lives
		# 4. APP_DIR = the root directory for a given version of the buskill app,
		#              which is 'buskill-<lin|win|mac>-<version>-x86_64' and:
		#                 [a] the dir containing the EXE_FILE file in Linux
		#                 [b] 1 dir above the dir containing the EXE_FILE in
		#                     Windows
		#                 [c] 2 dirs above the dir containing the EXE_FILE in
		#                     MacOS
		# 4. APPS_DIR = the directory where the app dirs live (one dir above
		#               APP_DIR)

		# get the absolute path to the file that the user executes to start buskill
		self.EXE_PATH = sys.executable

		# if the executable is actually just the python interpreter, then what
		# we want is the first argument
		if re.match( ".*python([1-9]\.?)*$", self.EXE_PATH ):
			self.EXE_PATH = os.path.abspath( sys.argv[0] )

		# split the EXE_PATH into dir & file parts
		self.EXE_DIR = os.path.split(self.EXE_PATH)[0]
		self.EXE_FILE = os.path.split(self.EXE_PATH)[1]

		# platform-specific setup
		if CURRENT_PLATFORM.startswith( 'LINUX' ):
			self.IS_PLATFORM_SUPPORTED = True
			self.OS_NAME_SHORT = 'lin'
			self.ARM_FUNCTION = self.armNix
			self.TRIGGER_FUNCTION = self.triggerLin

			# on Linux, the buskill AppImage is directly inside the APP_DIR
			self.APP_DIR = self.EXE_DIR

		if CURRENT_PLATFORM.startswith( 'WIN' ):
			self.IS_PLATFORM_SUPPORTED = True
			self.OS_NAME_SHORT = 'win'
			self.ARM_FUNCTION = self.armWin
			self.TRIGGER_FUNCTION = self.triggerWin

			# on Windows, the buskill binary is 1 dir below the APP_DIR
			self.APP_DIR = self.EXE_PATH.split( os.sep )[0:-2]
			self.APP_DIR = os.sep.join( self.APP_DIR )

		if CURRENT_PLATFORM.startswith( 'DARWIN' ):
			self.IS_PLATFORM_SUPPORTED = True
			self.OS_NAME_SHORT = 'mac'

			self.KERNEL_VERSION = str(platform.release()).split('.')[0]
			self.ARM_FUNCTION = self.armNix
			self.TRIGGER_FUNCTION = self.triggerMac

			# on MacOS, the binary is 2 dirs below the .app dir
			self.APP_DIR = self.EXE_PATH.split( os.sep )[0:-3]
			self.APP_DIR = os.sep.join( self.APP_DIR )

		# but if we're executing the code directly, then the APP_DIR is actually
		# one dir higher
		if self.EXE_FILE == 'main.py' and os.path.split(self.APP_DIR)[1] == 'src':
			self.APP_DIR = os.path.abspath(
			 os.path.join( self.APP_DIR, os.pardir)
			)

		# We package our .zip inside a single root dir to prevent zip-bombing.
		# When extracted on most platforms, this root dir is dropped into the
		# the cwd. But when using the Windows file Explorer GUI to extract
		# our .zip release, it actually creates an additional root dir with
		# the same name as our .zip file (minus the .zip extension). This
		# inconsistency means that we may have to go one dir up again
		if re.match(
		 "^buskill-" +str(self.OS_NAME_SHORT)+ "-.*",
		 self.APP_DIR.split(os.sep)[-2]
		):
			# the dir that we expected to be our APP_DIR is actually inside of
			# another dir that has the name "buskil-...", so let's make
			# *that* dir our APP_DIR

			self.APP_DIR = os.path.abspath(
			 os.path.join( self.APP_DIR, os.pardir)
			)

		# the APPS_DIR is one dir above the APP_DIR
		self.APPS_DIR = os.path.abspath( os.path.join(self.APP_DIR, os.pardir) )

		# update PATH to include the dir where main.py lives (the second one is
		# MacOS .app compatibility weirdness) so that we can find `gpg` there
		os.environ['PATH'] += \
		 os.pathsep+ self.EXE_DIR + \
		 os.pathsep+ self.APP_DIR

		# also update sys.python, so `import` statements will look in there (eg:
		# for upgraded_from.py)
		sys.path.append( self.EXE_DIR )

		msg = "DEBUG: EXE_PATH:|" +str(self.EXE_PATH)+  "|\n"
		msg+= "DEBUG: EXE_DIR:|" +str(self.EXE_DIR)+  "|\n"
		msg+= "DEBUG: EXE_FILE:|" +str(self.EXE_FILE)+  "|\n"
		msg+= "DEBUG: APP_DIR:|" +str(self.APP_DIR)+  "|\n"
		msg+= "DEBUG: APPS_DIR:|" +str(self.APPS_DIR)+  "|\n"
		msg+= "DEBUG: os.environ['PATH']:|" +str(os.environ['PATH'])+  "|\n"
		print( msg ); logger.debug( msg )

		# create a data dir in some safe place where we have write access
		# TODO: move this to main.py so the log file gets put in the CACHE_DIR
		# (that--or maybe just move the buskill.init() into main.py)
		self.setupDataDir()

		# handle conditions where this version was already upgraded by a newer
		# version or if this is a version that upgraded an older version
		self.handle_upgrades()

	# this function is necessary to be able to execute non-static methods on
	# the `self` instance of this object in a child process. Without this, we'll
	# get "TypeError: can't pickle weakref objects" errors in python >= 3.7.0
	# because some of the instance fields of this object are not pickleable
	#  * https://bugs.python.org/issue34034
	#  * https://docs.python.org/3/library/pickle.html#object.__reduce__
	#  * https://docs.python.org/3/library/pickle.html#object.__getstate__
	def __getstate__(self):

		state = self.__dict__.copy()

		msg = "DEBUG:__getstate__() pre:" +str( state.keys() )+ "|"
		print( msg ); logger.debug( msg )

		# remove instances of multiprocessing.Process() because they're not
		# pickleable
		unpickleable = [
		 'upgrade_process', 'usb_handler'
		]
		for instance_field in unpickleable:
			if instance_field in state:
				del state[instance_field]

		msg = "DEBUG:__getstate__() post:|" +str( state.keys() )+ "|"
		print( msg ); logger.debug( msg )

		return state

	# this is called when the GUI is closed 
	# TODO: use 'fuckit' python module https://stackoverflow.com/questions/63436916/how-to-ignore-exceptions-and-proceed-with-whole-blocks-multiple-lines-in-pytho/
	def close(self):

		# do what we can as fast as we can; don't get stuck by errors
		try:

			# if we don't kill this child process on exit, the UI will freeze
			try:
				self.usb_handler.kill()
			except ProcessLookupError as e:
				msg = "DEBUG: Ignoring ProcessLookupError " +str(e)
				msg += "\n\t" +str(e)+ "\n"
				print( msg ); logger.debug( msg )

			self.usb_handler.join()
		except:
			pass
		try:

			# if we don't kill this child process on exit, the UI will freeze
			try:
				self.upgrade_process.kill()
			except ProcessLookupError as e:
				msg = "DEBUG: Ignoring ProcessLookupError " +str(e)
				msg += "\n\t" +str(e)+ "\n"
				print( msg ); logger.debug( msg )

			self.upgrade_process.join()
		except:
			pass

		try:
			# delete cache dir
			self.wipeCache()
		except:
			pass

	def is_platform_supported(self):

		if self.OS_NAME_SHORT in ['lin','win','mac']:
			return True
		else:
			return False

	def handle_upgrades(self):

		# check to see if we're currently running a new version that is being
		# executed for the first time after replacing an old version
		if os.path.isfile( os.path.join( self.EXE_DIR, 'upgraded_from.py' ) ):
			from upgraded_from import UPGRADED_FROM
			if os.path.isdir( UPGRADED_FROM['APP_DIR'] ):

				msg = "DEBUG: Detected first-run of new version. Deleting old version."
				msg += "\n\t" +str(UPGRADED_FROM)+ "\n"
				print( msg ); logger.debug( msg )

				# only proceed with this delete if the dir matches what we'd expect
				if os.path.exists( os.path.join( UPGRADED_FROM['APP_DIR'], '.git' ) ):
					msg = "DEBUG: Cowardly refusing to recursively delete an app that actually looks like a git sandbox."
					print( msg ); logger.debug( msg )

				# note that this actually works for both *nix & windows and doesn't
				# fail with "unterminated character" errors
				#  * https://stackoverflow.com/a/54134464
				elif re.match( ".*buskill-[^\\" +os.sep+ "]*$", UPGRADED_FROM['APP_DIR'] ):

					# delete the old version's APP_DIR entirely
					self.UPGRADED_FROM = UPGRADED_FROM

					# don't exit on error
					try:

						# TODO: fix the restart on Windows so that the recursive
						#       delete after upgrade works and doesn't require a
						#       manual restart. See Also:
						#  * buskill_gui.py's handle_upgrades()
						#  * buskill_gui.py's upgrade5_restart()
						self.UPGRADED_FROM['DELETE_FAILED'] = False

						shutil.rmtree( self.UPGRADED_FROM['APP_DIR'] )

						# and delete the 'upgraded_from.py' file so we don't try to
						# delete the old version again
						os.unlink( os.path.join( self.EXE_DIR, 'upgraded_from.py' ) )

					except Exception as e:
						self.UPGRADED_FROM['DELETE_FAILED'] = True

						msg = "WARNING: Unable to delete old release (" +str(self.UPGRADED_FROM['APP_DIR'])+ ")"
						msg+= "\n\t" +str(e)
						print( msg ); logger.warn( msg )

				else:
					msg = "DEBUG: Cowardly refusing to recursively delete an old version that doesn't match our expected regex"
					print( msg ); logger.debug( msg )

		# check to see if we're currently running an old version whose
		# replacement version has already been installed
		if os.path.isfile( os.path.join( self.EXE_DIR, 'upgraded_to.py' ) ):
			from upgraded_to import UPGRADED_TO
			if os.path.exists( UPGRADED_TO['EXE_PATH'] ):
				self.UPGRADED_TO = UPGRADED_TO
				msg = "DEBUG: Detected that this version has already been upgraded. New version is:"
				msg += "\n\t" +str(self.UPGRADED_TO)+ "\n"
				print( msg ); logger.debug( msg )

	def setupDataDir(self):

		# first we choose where our data dir based on where we have write access
		data_dirs = list()

		# first try to create our data dir in the same dir that holds the dir
		# where the buskill app was installed (and where future updates will be
		# installed). This may be the BusKill USB drive itself.
		data_dirs.append( self.APPS_DIR )

		# Fall-back to the dir in which the executable is located
		data_dirs.append( self.APP_DIR )

		# finally, try the users's $HOME dir
		data_dirs.append( os.path.join( os.path.expanduser('~') ) )

		# iterate though our list of potential data dirs and pick the first one
		# that we can actually write to
		for data_dir in data_dirs:
			try:
				testfile = tempfile.TemporaryFile( dir=data_dir )
				testfile.close()
			except Exception as e:
				# we were unable to write to this data_dir; try the next one
				msg = "DEBUG: Unable to write to '" +data_dir+ "'; skipping."
				msg += "\n\t" +str(e)+ "\n"
				print( msg ); logger.debug( msg )
				continue

			# if we made it this far, we've confirmed that we can write to this
			# data_dir. store it and exit the loop; we'll use this one.
			self.DATA_DIR = os.path.join( data_dir, '.buskill' )
			break

		try:
			msg = "INFO: using DATA_DIR:|" +str(self.DATA_DIR)+ "|"
			print( msg ); logger.info( msg )
		except:
			msg = "WARNING: Unable to write to any DATA_DIR; not using one"
			print( msg ); logger.warn( msg )
			self.DATA_DIR = ''
			return

		# create cache dir (and clean if necessary) and data dir
		self.CACHE_DIR = os.path.join( self.DATA_DIR, 'cache' )
		self.wipeCache()

		contents = "This is a runtime cache dir for BusKill that is deleted every time the BusKill app is launched or exits.\n\nFor more information, see https://buskill.in\n"
		with open( os.path.join(self.CACHE_DIR, 'README.txt'), 'w' ) as fd:
			fd.write( contents )

		self.GNUPGHOME = os.path.join( self.CACHE_DIR, '.gnupg' )

	def toggle(self):

		if self.is_armed:
			msg = "DEBUG: attempting to disarm BusKill"
			print( msg ); logger.debug( msg )

			# disarm just means to terminate the child process in which the arm
			# function was spawned. this works on all platforms.
			try:
				self.usb_handler.kill()
				self.usb_handler.join()
			except:
				pass

			self.is_armed = False
			msg = "INFO: BusKill is disarmed."
			print( msg ); logger.info( msg )

		else:
			msg = "DEBUG: attempting to arm BusKill via " +str(self.ARM_FUNCTION)+ "()"
			print( msg ); logger.debug( msg )

			# launch an asynchronous child process that'll loop and listen for
			# usb events
#			self.usb_handler = self.Process(
			self.usb_handler = multiprocessing.Process(
			 target = self.ARM_FUNCTION
			)
			self.usb_handler.start()

			self.is_armed = True
			msg = "INFO: BusKill is armed. Listening for removal event.\n"
			msg+= "INFO: To disarm the CLI, exit with ^C or close this terminal"
			print( msg ); logger.info( msg )

	# this is a callback function that is registered to be called when a usb
	# hotplug event occurs using libusb (linux & macos)
	def hotplugCallbackNix( self, *argv ):

		(context, device, event) = argv

		msg = "DEBUG: called hotplugCallbackNix()"
		print( msg ); logger.debug( msg )

		msg = "context:|" +str(context)+ "|"
		print( msg ); logger.debug( msg )

		msg = "device:|" +str(device)+ "|"
		print( msg ); logger.debug( msg )

		msg = "event:|" +str(event)+ "|"
		print( msg ); logger.debug( msg )

		msg = "usb1.HOTPLUG_EVENT_DEVICE_LEFT:|" +str(usb1.HOTPLUG_EVENT_DEVICE_LEFT)+ "|"
		print( msg ); logger.debug( msg )

		# is this from a usb device being inserted or removed? 
		if event == usb1.HOTPLUG_EVENT_DEVICE_LEFT:
			# this is a usb removal event

			msg = "calling " +str(self.TRIGGER_FUNCTION)
			print( msg ); logger.debug( msg )

			self.TRIGGER_FUNCTION()

	####################
	# ARMING FUNCTIONS #
	####################

	# this works for both linux and mac
	def armNix(self):

		with usb1.USBContext() as context:

			if not context.hasCapability(usb1.CAP_HAS_HOTPLUG):
				msg = 'ERROR: Hotplug support is missing'
				print( msg ); logger.error( msg )
				return msg

			opaque = context.hotplugRegisterCallback( self.hotplugCallbackNix )

			try:
				while True:
					# this call is blocking (with a default timeout of 60 seconds)
					# afaik there's no way to tell USBContext.handleEvents() to exit
					# safely, so instead we just make the whole call to this arming
					# function in a new child process and kill it on disarm with
					# kill() this approach isn't very nice and it dumps a
					# traceback to output, but it *does* immediately disarm without
					# having wait for the timeout..
					context.handleEvents()

			except (KeyboardInterrupt, SystemExit) as e:
				msg = "DEBUG: Exiting armNix() loop: " +str(e)
				print( msg ); logger.info( msg )

		return 0

	def armWin(self):

		w = Notification( self )
		win32gui.PumpMessages()

	#####################
	# TRIGGER FUNCTIONS #
	#####################

	# TODO: add other triggers besides lockscreens

	def triggerLin(self):
		msg = "DEBUG: BusKill lockscreen trigger executing now"
		print( msg ); logger.debug( msg )

		try:
			subprocess.run( ['xdg-screensaver', 'lock'] )
			subprocess.run( ['xscreensaver', '-lock'] )
		except FileNotFoundError as e:
			pass

	def triggerWin(self):
		msg = "DEBUG: BusKill lockscreen trigger executing now"
		print( msg ); logger.debug( msg )

		windll.user32.LockWorkStation()

	def triggerMac(self):
		msg = "DEBUG: BusKill lockscreen trigger executing now"
		print( msg ); logger.info( msg )

		try:
			# this should work for most MacOS versions
			subprocess.run( ['/System/Library/CoreServices/Menu Extras/user.menu/Contents/Resources/CGSession', '-suspend'] ) 

		except Exception as e:

			try:
				# fall-back on `pmset`
				subprocess.run( ['pmset', 'displaysleepnow'] )

			except Exception as e:
				msg = "ERROR: Mac Kernel" + self.KERNEL_VERSION + "Unsupported"
				print( msg ); logger.error(msg)

	#####################
	# UPGRADE FUNCTIONS #
	#####################

#	import pickle
#	class MyPickler (pickle.Pickler):
#		def save(self, obj):
#			try:
#				pickle.Pickler.save(self, obj)
#			except Exception as e:
#				import pdb;pdb.set_trace()

	# allow us to catch exceptions inside child processes
	# * https://stackoverflow.com/questions/63758186/how-to-catch-exceptions-thrown-by-functions-executed-using-multiprocessing-proce
	class Process(multiprocessing.Process):

		def __init__(self, *args, **kwargs):
			multiprocessing.Process.__init__(self, *args, **kwargs)
			self._pconn, self._cconn = multiprocessing.Pipe()
			self._exception = None

		def run(self):

			try: 
				multiprocessing.Process.run(self)
				self._cconn.send(None)

			except Exception as e:
				msg = "DEBUG: Exception thrown in child process: " +str(e)+ "\n"
				print( msg ); logger.debug( msg )

				tb = traceback.format_exc()

				msg = "DEBUG: Traceback: " +str(tb)
				print( msg ); logger.debug( msg )

				self._cconn.send((e, tb))

		@property
		def exception(self):
			if self._pconn.poll():
				self._exception = self._pconn.recv()
			return self._exception

	def wipeCache(self):

		# first umount anything in the cache dir
		try:
			dmg_mnt_path = os.path.join( self.CACHE_DIR, 'dmg_mnt' )
			if os.path.exists( dmg_mnt_path ) and self.OS_NAME_SHORT == 'mac':
				subprocess.run( ['umount', dmg_mnt_path] )
		except:
			pass

		if os.path.exists( self.CACHE_DIR ):
			shutil.rmtree( self.CACHE_DIR )

		try:
			os.makedirs( self.CACHE_DIR, mode=0o700 )
			os.chmod( self.DATA_DIR, mode=0o0700 )
		except:
			pass

	# Takes the path (as a string) to a SHA256SUMS file and a list of paths to
	# local files. Returns true only if all files' checksums are present in the
	# SHA256SUMS file and their checksums match
	def integrity_is_ok( self, sha256sums_filepath, local_filepaths ):

		# first we parse the SHA256SUMS file and convert it into a dictionary
		sha256sums = dict()
		with open( sha256sums_filepath ) as fd:
			for line in fd:
				# sha256 hashes are exactly 64 characters long
				checksum = line[0:64]

				# there is one space followed by one metadata character between the
				# checksum and the filename in the `sha256sum` command output
				filename = os.path.split( line[66:] )[1].strip()
				sha256sums[filename] = checksum

		msg = 'DEBUG: sha256sums:|' +str(sha256sums)+ '|'
		print( str(msg) ); logger.debug( msg )

		# now loop through each file that we were asked to check and confirm its
		# checksum matches what was listed in the SHA256SUMS file
		for local_file in local_filepaths:

			local_filename = os.path.split( local_file )[1]

			sha256sum = sha256()
			with open( local_file, 'rb' ) as fd:
	  			data_chunk = fd.read(1024)
	  			while data_chunk:
	  				sha256sum.update(data_chunk)
	  				data_chunk = fd.read(1024)

			checksum = sha256sum.hexdigest()

			msg = 'DEBUG: checksum:|' +str(checksum)+ "|\n"
			msg+= 'DEBUG: sha256sums[local_filename]:|' +str(sha256sums[local_filename])+ '|'
			print( str(msg) ); logger.debug( msg )

			if checksum != sha256sums[local_filename]:
				return False

		return True

	def get_upgrade_status(self):

		# is the message (upgrade_status_msg) a string that we can read from
		# directly (running synchronously) or a multiprocessing.Array() because
		# upgrade() is in an asymmetric child process?
		if self.upgrade_status_msg == None or \
		 type(self.upgrade_status_msg) == str:
			# it's just a string; read from it directly
			return str(self.upgrade_status_msg)
		else:
			# it's shared memory; write to it correctly
			return self.upgrade_status_msg.value.decode('utf-8')

	def set_upgrade_status(self, new_msg):

		# is the destination (upgrade_status_msg) a string that we can write to
		# directly (running synchronously) or a multiprocessing.Array() because
		# upgrade() is in an asymmetric child process?
		if self.upgrade_status_msg == None or \
		 type(self.upgrade_status_msg) == str:
			# it's just a string; write to it directly
			self.upgrade_status_msg = new_msg
		else:
			# it's shared memory; read from it correctly
			self.upgrade_status_msg.value = bytes(new_msg, 'utf-8')

	# helper function that executes upgrade() in the background because kivy
	# apps cannot https://github.com/kivy/kivy/issues/1116
	#
	# Note: if you use this function, then you should make sure to call
	#       get_upgrade_result() after it's done to free() the child's resources
	#
	# TODO: maybe one day this function can be eliminated and instead the client
	# can merely execute upgrade() directly in a thread. But that would require
	# rewriting upgrade() to catch sentinels so it can kill itself
	def upgrade_bg(self):

		# if we're running upgrade() synchronously, then upgrade() can access our
		# object's instance fields OK. But if we run upgrade() in the background,
		# then the child process won't be able to write to our instance fields as
		# strings (well, only a copy of them that's not shared), and we have to 
		# change the strings to shared memory using ctypes arrays
		self.upgrade_status_msg = multiprocessing.Array( 'c', 256 )
		self.upgrade_result = multiprocessing.Array( 'c', 256 )

		#upgrade_pool = multiprocessing.Pool( processes=1 )
		#upgrade_process = upgrade_pool.apply_async( upgrade )

		# Note: We're using multiprocessing.Process() instead of threads or
		# multiprocessing.Pool() becaus we can get the pid and os.kill() a 
		# child process. The downsides of this is that we have to use shared
		# memory and we can't specify a callback when it finishes.

		self.upgrade_process = self.Process(
#		self.upgrade_process = multiprocessing.Process(
		 target = self.upgrade
		)
		self.upgrade_process.start()

	def upgrade_bg_terminate(self):

		self.upgrade_process.kill()
		self.upgrade_process.join()

		# cleanup
		self.upgrade_process = None
		self.upgrade_status_msg = None
		self.upgrade_result = None

	def upgrade_is_finished(self):

		if self.upgrade_process.is_alive():
			return False

		return True

	# this function should be called at the end of upgrade() with its return
	# this is a hack that effectively allows us to get a value returned from
	# a function that's executed in a child process using the multiprocessing
	# module. On success, upgrade_result will be the absolute filepath to the
	# newly-installed executable after upgrade(). On failure it will be:
	#  1  = No new updates available
	def set_upgrade_result(self, upgrade_result):

		# are we being called from inside a child process that needs to use
		# shared memory? Or is it just a string?
		if self.upgrade_result == None or \
		 type(self.upgrade_result) in [str,int]:
			# it's just a string; write to it directly
			self.upgrade_result = upgrade_result
		else:
			# it's shared memory; read from it correctly
			self.upgrade_result.value = bytes(str(upgrade_result), 'utf-8')

		return upgrade_result

	def get_upgrade_result(self):

#		if self.upgrade_pool.is_alive():
		if not self.upgrade_is_finished():
			msg = 'upgrade() is still running'
			print( "DEBUG: " + msg ); logger.debug( msg )
			raise RuntimeWarning( msg )

		# TODO; confirm that merely dereferencing this pointer to the ctypes array
		# built using multiprocessing.Array() is sufficient to let it be free()ed
		# later by the garbage collector (?)
		#  * https://stackoverflow.com/questions/63757092/how-to-cleanup-free-memory-when-using-multiprocessing-array-in-python

		# take any exceptions raised within upgrade() and raise them now
		if self.upgrade_process.exception:
			exception, traceback = self.upgrade_process.exception

			self.upgrade_process.join()
			self.upgrade_process = None
			self.upgrade_status_msg = None
			self.upgrade_result = None
			self.wipeCache()

			raise exception
	
		if self.upgrade_result == None or \
		 type(self.upgrade_result) in [str,int]:
			# it's just a string; write to it directly
			upgrade_result = str(self.upgrade_result)
		else:
			upgrade_result = str(self.upgrade_result.value.decode('utf-8'))

		# cleanup
		self.upgrade_process.join()
		self.upgrade_process = None
		self.upgrade_status_msg = None
		self.upgrade_result = None
		self.wipeCache()
	
		self.UPGRADED_TO = { 'EXE_PATH': upgrade_result }
		return upgrade_result

	def upgrade(self):

		self.set_upgrade_status( "Starting Upgrade.." )
		msg = "DEBUG: Called upgrade()"
		print( msg ); logger.debug( msg )

		# Note: While this upgrade solution does cryptographically verify the
		# authenticity and integrity of new versions, it is still vulnerable to
		# at least the following attacks:
		# 
		#  1. Freeze attacks
		#  2. Slow retrieval attacks
		#
		# The fix to this is to upgrade to TUF, once it's safe to do so. In the
		# meantime, these attacks are not worth mitigating because [a] this app
		# never auto-updates; it's always requires user input, [b] our app  in
		# general is low-risk; it doesn't even access the internet outside of the
		# update process, and [c] these attacks aren't especially severe

		# TODO: switch to using TUF once TUF no longer requires us to install
		#       untrusted software onto our cold-storage machine holding our
		#       release private keys. For more info, see:
		# 
		#  * https://github.com/BusKill/buskill-app/issues/6
		#  * https://github.com/theupdateframework/tuf/issues/1109

		#########################
		# UPGRADE SANITY CHECKS #
		#########################

		# only upgrade on linux, windows, and mac
		if self.OS_NAME_SHORT == '':
			msg = 'Upgrades not supported on this platform (' +CURRENT_PLATFORM+ ')'
			print( "DEBUG: " + msg ); logger.debug( msg )
			raise RuntimeWarning( msg )

		# skip upgrade if we can't write to disk
		if self.DATA_DIR == '':
			msg = 'Unable to upgrade. No DATA_DIR.'
			print( "DEBUG: " + msg ); logger.debug( msg )
			raise RuntimeWarning( msg )

		# make sure we can write to the dir where the new versions will be
		# extracted
		if not os.access(self.APPS_DIR, os.W_OK):
			msg = 'Unable to upgrade. APPS_DIR not writeable (' +str(self.APPS_DIR)+ ')'
			print( "DEBUG: " + msg ); logger.debug( msg )
			raise RuntimeWarning( msg )

		# make sure we can delete the executable itself
		if not os.access( os.path.join(self.EXE_DIR, self.EXE_FILE), os.W_OK):
			msg = 'Unable to upgrade. EXE_FILE not writeable (' +str( os.path.join(self.EXE_DIR, self.EXE_FILE) )+ ')'
			print( "DEBUG: " + msg ); logger.debug( msg )
			raise RuntimeWarning( msg )

		#############
		# SETUP GPG #
		#############

		# first, start with a clean cache
		self.wipeCache()

		# prepare our ephemeral gnupg home dir so we can verify the signature of our
		# checksum file after download and before "install"
		if os.path.exists( self.GNUPGHOME ):
			shutil.rmtree( self.GNUPGHOME )
		os.makedirs( self.GNUPGHOME, mode=0o700 )
		os.chmod( self.GNUPGHOME, mode=0o0700 )

		# get the contents of the KEYS file shipped with our software
		try:
			with open( os.path.join(APP_DIR, 'KEYS'), 'r' ) as fd:
				KEYS = fd.read()
		except:
			# fall-back to one dir up if we're executing from 'src/'
			with open( os.path.join( os.path.split(APP_DIR)[0], 'KEYS'), 'r' ) as fd:
				KEYS = fd.read()

		gpg = gnupg.GPG( gnupghome=self.GNUPGHOME )
		gpg.import_keys( KEYS )

		############################
		# DETERMINE LATEST VERSION #
		############################

		metadata_filepath = os.path.join( self.CACHE_DIR, 'meta.json' )
		signature_filepath = os.path.join( self.CACHE_DIR, 'meta.json.asc' )

		# loop through each of our mirrors until we get one that's online
		metadata = ''
		random.shuffle(UPGRADE_MIRRORS)
		for mirror in UPGRADE_MIRRORS:

			# break out of loop if we've already downloaded the metadata from
			# some mirror in our list
			if os.path.exists( metadata_filepath ) \
			 and os.path.exists( signature_filepath ):
				break

			self.set_upgrade_status( "Polling for latest update" )
			msg = "DEBUG: Checking for updates at '" +str(mirror)+ "'"
			print( msg ); logger.debug( msg )

			# try to download the metadata json file and its detached signature
			files = [ mirror, mirror + '.asc' ]
			for f in files:

				filename = f.split('/')[-1]
				filepath = os.path.join( self.CACHE_DIR, filename )

				try:
					with urllib.request.urlopen( f, cafile=certifi.where() ) as url, \
					 open( filepath, 'wb' ) as out_file:
		
						# the metadata definitely shouldn't be more than 1 MB
						size_bytes = int(url.info().get('content-length'))
						if size_bytes > 1048576:
							msg = "\tMetadata too big; skipping (" +str(size_bytes)+ " bytes)"
							print( msg ); logger.debug( msg )
							break
		
						shutil.copyfileobj(url, out_file)
						continue

				except Exception as e:
					msg = "\tFailed to fetch data from mirror; skipping (" +str(e)+ ")"
					print( msg ); logger.debug( msg )
					break

		# CHECK SIGNATURE OF METADATA

		self.set_upgrade_status( "Verifying metadata signature" )
		msg = "\tDEBUG: Finished downloading update metadata. Checking signature."
		print( msg ); logger.debug( msg )
			
		# open the detached signature and check it with gpg
		with open( signature_filepath, 'rb' ) as fd:
			verified = gpg.verify_file( fd, metadata_filepath )

		# check that this main signature fingerprint meets our expectations
		# bail if it a key was used other than the one we require
		if verified.fingerprint != RELEASE_KEY_SUB_FINGERPRINT:
			self.wipeCache()
			msg = 'ERROR: Invalid signature fingerprint (expected '+str(RELEASE_KEY_SUB_FINGERPRINT)+' but got '+str(verified.fingerprint)+')! Please report this as a bug.'
			print( msg ); logger.debug( msg )
			raise RuntimeError( msg )

		# extract from our list of signatures any signatures made with exactly the
		# keys we'd expect (check the master key and the subkey fingerprints)
		sig_info = [ verified.sig_info[key] for key in verified.sig_info if verified.sig_info[key]['fingerprint'] == RELEASE_KEY_SUB_FINGERPRINT and verified.sig_info[key]['pubkey_fingerprint'] == RELEASE_KEY_FINGERPRINT ]

		# if we couldn't find a signature that matched our requirements, bail
		if sig_info == list():
			self.wipeCache()
			msg = 'ERROR: No valid signature found! Please report this as a bug.'
			print( msg ); logger.debug( msg )
			raise RuntimeError( msg )

		else:
			sig_info = sig_info.pop()

		# check both the list of signatures and this other one. why not?
		# bail if either is an invalid signature
		if verified.status != 'signature valid':
			self.wipeCache()
			msg = 'ERROR: No valid signature found! Please report this as a bug (' +str(sig_info)+ ').'
			print( msg ); logger.debug( msg )
			raise RuntimeError( msg )

		if sig_info['status'] != 'signature valid':
			self.wipeCache()
			msg = 'ERROR: No valid sig_info signature found! Please report this as a bug (' +str(sig_info)+ ').'
			print( msg ); logger.debug( msg )
			raise RuntimeError( msg )

		msg = "\tDEBUG: Signature is valid (" +str(sig_info)+ ")."
		print( msg ); logger.debug( msg )

		# try to load the metadata (this is done after signature so we don't load
		# something malicious that may attack the json.loads() parser)
		try:
			with open( metadata_filepath, 'r' ) as fd:
				metadata = json.loads( fd.read() ) 
		except Exception as e:
			msg = 'Unable to upgrade. Could not fetch metadata file (' +str(e)+ '.'
			print( "DEBUG: " + msg ); logger.debug( msg )
			raise RuntimeWarning( msg )
			
		# abort if it's empty
		if metadata == '':
			msg = 'Unable to upgrade. Could not fetch metadata contents.'
			print( "DEBUG: " + msg ); logger.debug( msg )
			raise RuntimeWarning( msg )

		###########################
		# DOWNLOAD LATEST VERSION #
		###########################

		# the only reason the SOURCE_DATE_EPOCH would be missing is if we're executing
		# the python files directly (eg we're testing) and we can just get it from git
		if BUSKILL_VERSION['SOURCE_DATE_EPOCH'] == '':
			result = subprocess.run( [
			 'git',
			 '--git-dir=/home/user/sandbox/buskill-app/.git',
			 'log',
			 '-1',
			 '--pretty=%ct'
			], capture_output = True )
			BUSKILL_VERSION['SOURCE_DATE_EPOCH'] = int( result.stdout )

		# check metadata to see if there's a newer version than what we're running
		latestRelease = metadata['latest']['buskill-app']['stable']
		currentRelease = BUSKILL_VERSION['VERSION']

		msg = "DEBUG: Current version: " +str(currentRelease)+ ".\n"
		msg += "DEBUG: Latest version: " +str(latestRelease)+ "."
		print( msg ); logger.debug( msg )

		if LooseVersion(latestRelease) <= LooseVersion(currentRelease):
			msg = "INFO: Current version is latest version. No new updates available."
			print( msg ); logger.info( msg )
			return self.set_upgrade_result( 1 )

		# currently we only support x86_64 builds..
		arch = 'x86_64'

		sha256sums_urls = metadata['updates']['buskill-app'][str(latestRelease)]['SHA256SUMS']
		sha256sums_filepath = os.path.join( self.CACHE_DIR, 'SHA256SUMS' )

		signature_urls = metadata['updates']['buskill-app'][str(latestRelease)]['SHA256SUMS.asc']
		signature_filepath = os.path.join( self.CACHE_DIR, 'SHA256SUMS.asc' )

		archive_urls = metadata['updates']['buskill-app'][str(latestRelease)][self.OS_NAME_SHORT][arch]['archive']['url']
		archive_filename = archive_urls[0].split('/')[-1]
		archive_filepath = os.path.join( self.CACHE_DIR, archive_filename )

		# shuffle all three URLs but shuffle them the same
		start_state = random.getstate()
		random.shuffle( archive_urls )
		random.setstate( start_state)
		random.shuffle( sha256sums_urls )
		random.setstate( start_state)
		random.shuffle( signature_urls )
		random.setstate( start_state)

		# loop through each of our downloads
		files = [ signature_urls, sha256sums_urls, archive_urls ]
		for f in files:

			# break out of loop if we've already all necessary files from
			# some mirror in our list
			if os.path.exists( archive_filepath ) \
			 and os.path.exists( sha256sums_filepath ) \
			 and os.path.exists( signature_filepath ): \
				break

			# try to download the metadata json file and its detached signature
			for download in f:

				msg = "DEBUG: Attempting to download '" +str(download)+ "'"
				print( msg ); logger.debug( msg )

				filename = download.split('/')[-1]
				filepath = os.path.join( self.CACHE_DIR, filename )

				try:
					with urllib.request.urlopen( download, cafile=certifi.where() ) as url, \
					 open( filepath, 'wb' ) as out_file:
		
						# don't download any files >200 MB
						size_bytes = int(url.info().get('content-length'))
						self.set_upgrade_status( "Downloading " +str(filename)+ " (" +str(math.ceil(size_bytes/1024/1024))+ "MB)" )
						if size_bytes > 209715200:
							msg = "\tFile too big; skipping (" +str(size_bytes)+ " bytes)"
							print( msg ); logger.debug( msg )
							continue
		
						shutil.copyfileobj(url, out_file)
						msg = "\tDone"
						print( msg ); logger.debug( msg )
						break

				except Exception as e:
					msg = "\tFailed to download update; skipping (" +str(e)+ ")"
					print( msg ); logger.debug( msg )
					continue

		####################
		# VERIFY SIGNATURE #
		####################

		self.set_upgrade_status( "Verifying signature" )
		msg = "DEBUG: Finished downloading update files. Checking signature."
		print( msg ); logger.debug( msg )

		# open the detached signature and check it with gpg
		with open( signature_filepath, 'rb' ) as fd:
			verified = gpg.verify_file( fd, sha256sums_filepath )

		# check that this main signature fingerprint meets our expectations
		# bail if it a key was used other than the one we require
		if verified.fingerprint != RELEASE_KEY_SUB_FINGERPRINT:
			self.wipeCache()
			msg = 'ERROR: Invalid signature fingerprint (expected '+str(RELEASE_KEY_SUB_FINGERPRINT)+' but got '+str(verified.fingerprint)+')! Please report this as a bug.'
			print( msg ); logger.debug( msg )
			raise RuntimeError( msg )

		# extract from our list of signatures any signatures made with exactly the
		# keys we'd expect (check the master key and the subkey fingerprints)
		sig_info = [ verified.sig_info[key] for key in verified.sig_info if verified.sig_info[key]['fingerprint'] == RELEASE_KEY_SUB_FINGERPRINT and verified.sig_info[key]['pubkey_fingerprint'] == RELEASE_KEY_FINGERPRINT ]

		# if we couldn't find a signature that matched our requirements, bail
		if sig_info == list():
			self.wipeCache()
			msg = 'ERROR: No valid signature found! Please report this as a bug.'
			print( msg ); logger.debug( msg )
			raise RuntimeError( msg )

		else:
			sig_info = sig_info.pop()

		# check both the list of signatures and this other one. why not?
		# bail if either is an invalid signature
		if verified.status != 'signature valid':
			self.wipeCache()
			msg = 'ERROR: No valid signature found! Please report this as a bug (' +str(sig_info)+ ').'
			print( msg ); logger.debug( msg )
			raise RuntimeError( msg )

		if sig_info['status'] != 'signature valid':
			self.wipeCache()
			msg = 'ERROR: No valid sig_info signature found! Please report this as a bug (' +str(sig_info)+ ').'
			print( msg ); logger.debug( msg )
			raise RuntimeError( msg )

		msg = "DEBUG: Signature is valid (" +str(sig_info)+ ")."
		print( msg ); logger.debug( msg )

		####################
		# VERIFY INTEGRITY #
		####################

		if not self.integrity_is_ok( sha256sums_filepath, [ archive_filepath ] ):
			self.wipeCache()
			msg = 'ERROR: Integrity check failed. '
			print( msg ); logger.debug( msg )
			raise RuntimeError( msg )

		self.set_upgrade_status( "Verifying integrity" )
		msg = "DEBUG: New version's integrity is valid."
		print( msg ); logger.debug( msg )

		###########
		# INSTALL #
		###########
		
		self.set_upgrade_status( "Extracting archive" )
		msg = "DEBUG: Extracting '" +str(archive_filepath)+ "' to '" +str(self.APPS_DIR)+ "'"
		print( msg ); logger.debug( msg )

		if self.OS_NAME_SHORT == 'lin':
		
			import tarfile
			with tarfile.open( archive_filepath ) as archive_tarfile:

				# get the path to the new executable
				new_version_exe = [ file for file in archive_tarfile.getnames() if re.match( ".*buskill-[^/]+\.AppImage$", file ) ][0]
				new_version_exe = self.APPS_DIR + '/' + new_version_exe
				archive_tarfile.extractall( path=self.APPS_DIR )

		elif self.OS_NAME_SHORT == 'win':

			import zipfile
			with zipfile.ZipFile( archive_filepath ) as archive_zipfile:

				# get the path to the new executable
				new_version_exe = [ file for file in archive_zipfile.namelist() if re.match( ".*buskill\.exe$", file ) ][0]
				new_version_exe = self.APPS_DIR + '\\' + new_version_exe

				archive_zipfile.extractall( path=self.APPS_DIR )

		elif self.OS_NAME_SHORT == 'mac':

			# create a new dir where we'll mount the dmg temporarily (since we can't
			# extract DMGs and the python modules for extracting 7zip archives
			# has many dependencies [so we don't use it])
			dmg_mnt_path = os.path.join( self.CACHE_DIR, 'dmg_mnt' )
			os.makedirs( dmg_mnt_path, mode=0o700 )
			os.chmod( dmg_mnt_path, mode=0o0700 )

			# mount the dmg, copy the .app out, and unmount
			subprocess.run( ['hdiutil', 'attach', '-mountpoint', dmg_mnt_path, archive_filepath] )
			app_path = os.listdir( dmg_mnt_path ).pop()
			shutil.copytree( dmg_mnt_path +'/'+ app_path, self.APPS_DIR + '/' + app_path )
			subprocess.run( ['hdiutil', 'detach', dmg_mnt_path] )

			new_version_exe = self.APPS_DIR+ '/' +app_path+ '/Contents/MacOS/buskill'

		# create a file in new version's EXE_DIR so that it will know where the
		# old version lives and be able to delete it on its first execution
		contents = { 'APP_DIR': self.APP_DIR }
		new_version_exe_dir = os.path.abspath(
		 os.path.join( new_version_exe, os.pardir)
		)
		with open( os.path.join( new_version_exe_dir, 'upgraded_from.py' ), 'w' ) as fd:
			fd.write( 'UPGRADED_FROM = ' +str(contents) )
		
		# create a file in this current (now outdated) version's EXE_DIR so that
		# it will be able to prompt the user to execute the newer version if they
		# open this older version by mistake in the future
		self.UPGRADED_TO = { 'EXE_PATH': new_version_exe }
		with open( os.path.join( self.EXE_DIR, 'upgraded_to.py' ), 'w' ) as fd:
			fd.write( 'UPGRADED_TO = ' +str(self.UPGRADED_TO) )

		msg = "INFO: Installed new version executable to  '" +str(new_version_exe)
		print( msg ); logger.info( msg )

		return self.set_upgrade_result( new_version_exe )
