#!/usr/bin/env python3.7
"""
::

  File:    buskill.py
  Authors: Michael Altfield <michael@buskill.in>
  Created: 2020-06-23
  Updated: 2020-08-09
  Version: 0.2

This is the heart of the buskill app, shared by both the cli and gui

For more info, see: https://buskill.in/
"""

################################################################################
#                                   IMPORTS                                    #
################################################################################

import platform, multiprocessing, subprocess
import urllib.request, json, certifi, sys, os, shutil, tempfile, random, gnupg
from buskill_version import BUSKILL_VERSION

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
#                                  FUNCTIONS                                   #
################################################################################

def init():

	global buskill_is_armed
	buskill_is_armed = False

	global usb_handler

	global ERR_PLATFORM_NOT_SUPPORTED
	ERR_PLATFORM_NOT_SUPPORTED = 'ERROR: Your platform (' +str(platform.system())+ ') is not supported. If you believe this is an error, please file a bug report:\n\nhttps://github.com/BusKill/buskill-app/issues'

	# update PATH to include the dir where main.py lives (the second one is MacOS
	# .app compatibility weirdness) so that we can find `gpg` there
	os.environ['PATH'] += \
	 os.pathsep+ APP_DIR + \
	 os.pathsep+ os.path.split(APP_DIR)[0]

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

	# create a data dir in some safe place where we have write access
	# TODO: move this to main.py so the log file gets put in the CACHE_DIR
	# (that--or maybe just move the buskill.init() into main.py)
	global DATA_DIR, CACHE_DIR, GNUPGHOME
	setupDataDir()

# this is called when the GUI is closed 
# TODO: use 'fuckit' python module https://stackoverflow.com/questions/63436916/how-to-ignore-exceptions-and-proceed-with-whole-blocks-multiple-lines-in-pytho/
def close():

	# do what we can as fast as we can; don't get stuck by errors
	try:

		# if we don't kill this child process on exit, the UI will freeze
		usb_handler.terminate()
		usb_handler.join()
	except:
		pass

	try:
		# delete cache dir
		if os.path.exists( CACHE_DIR ):
			shutil.rmtree( CACHE_DIR )
	except:
		pass


def isPlatformSupported():

	if CURRENT_PLATFORM.startswith( 'LINUX' ) \
	 or CURRENT_PLATFORM.startswith( 'WIN' ) \
	 or CURRENT_PLATFORM.startswith( 'DARWIN' ):
		return True
	else:
		return False

def setupDataDir():

	global DATA_DIR, CACHE_DIR, GNUPGHOME

	# first we choose where our data dir based on where we have write access
	data_dirs = list()

	# first try to create our data dir in the same dir in which <this> python
	# script is located
	data_dirs.append( sys.path[0] )

	# Fall-back to the dir in which the executable is located. This is mainly for
	# AppImages since their src files are in a read-only squashfs. But only use
	# this if the executable 'buskill.AppImage' or 'buskill.exe'. Don't use it if
	# the executable is 'python' as we don't want our data dir in /usr/bin/
	exe_dir = os.path.split(sys.executable)
	if not 'python' in exe_dir[1]:
		data_dirs.append( exe_dir[0] )

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
			print( msg ); logging.debug( msg )
			continue

		# if we made it this far, we've confirmed that we can write to this
		# data_dir. store it and exit the loop; we'll use this one.
		DATA_DIR = os.path.join( data_dir, '.buskill' )
		break

	try:
		msg = "INFO: using DATA_DIR:|" +str(DATA_DIR)+ "|"
		print( msg ); logging.info( msg )
	except:
		msg = "WARNING: Unable to write to any DATA_DIR; not using one"
		print( msg ); logging.warn( msg )
		DATA_DIR = ''
		return

	# create cache dir (and clean if necessary) and data dir
	CACHE_DIR = os.path.join( DATA_DIR, 'cache' )
	if os.path.exists( CACHE_DIR ):
		shutil.rmtree( CACHE_DIR )
	os.makedirs( CACHE_DIR, mode=0o700 )
	os.chmod( DATA_DIR, mode=0o0700 )

	contents = "This is a runtime cache dir for BusKill that is deleted every time the BusKill app is launched or exits.\n\nFor more information, see https://buskill.in\n"
	with open( os.path.join(CACHE_DIR, 'README.txt'), 'w' ) as fd:
		fd.write( contents )

	GNUPGHOME = os.path.join( CACHE_DIR, '.gnupg' )

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
		msg = "INFO: BusKill is armed. Listening for removal event.\n"
		msg+= "INFO: To disarm the CLI, exit with ^C or close this terminal"
		print( msg ); logger.info( msg )

# this is a callback function that is registered to be called when a usb
# hotplug event occurs using libusb (linux & macos)
def hotplugCallbackNix( *argv ):

	# the global scope variables appear to be undefined when this function is
	# called by libusb for some reason, so we have to add this platform logic
	# directly in this function too
	CURRENT_PLATFORM = platform.system().upper()
	if CURRENT_PLATFORM.startswith( 'LINUX' ):
		trigger_fun = triggerLin

	if CURRENT_PLATFORM.startswith( 'DARWIN' ):
		trigger_fun = triggerMac

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

		msg = "calling " +str(trigger_fun)
		print( msg ); logger.debug( msg )

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
	msg = "DEBUG: BusKill lockscreen trigger executing now"
	print( msg ); logger.info( msg )

	try:
		subprocess.run( ['pmset', 'displaysleepnow'] )
	except FileNotFoundError as e:
		subprocess.run( ['/System/Library/CoreServices/Menu Extras/user.menu/Contents/Resources/CGSession', '-suspend'] )

def upgrade():

	msg = "DEBUG: Called upgrade()"
	print( msg ); logging.debug( msg )

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
	os_name_short = ''
	if CURRENT_PLATFORM.startswith( 'LINUX' ):
		os_name_short = 'lin'
	if CURRENT_PLATFORM.startswith( 'WIN' ):
		os_name_short = 'win'
	if CURRENT_PLATFORM.startswith( 'DARWIN' ):
		os_name_short = 'mac'
	if os_name_short == '':
		raise RuntimeWarning( 'Upgrades not supported on this platform(' +CURRENT_PLATFORM+ ')' )

	# get the absolute path to the file that the user executes to start buskill
	EXE_PATH = sys.executable
	EXE_DIR = os.path.split(EXE_PATH)[0]
	EXE_FILE = os.path.split(EXE_PATH)[1]
	# TODO: uncomment this block
#	if EXE_FILE != 'buskill.AppImage' \
#	 or EXE_FILE != 'buskill' \
#	 or EXE_FILE != 'buskill.exe':
#		raise RuntimeWarning( 'Unsupported executable (' +EXE_PATH+ ')' )

	# skip upgrade if we can't write to disk
	if DATA_DIR == '':
		raise RuntimeWarning( 'Unable to upgrade. No DATA_DIR.' )

	# make sure we can write to the dir where the executable lives
	if not os.access(EXE_DIR, os.W_OK):
		raise RuntimeWarning( 'Unable to upgrade. EXE_DIR not writeable (' +str(EXE_DIR)+ ')' )

	# make sure we can overwrite the executable itself
	# TODO: uncomment this block
#	if not os.access(EXE_FILE, os.W_OK):
#		raise RuntimeWarning( 'Unable to upgrade. EXE_FILE not writeable (' +str(EXE_FILE)+ ')' )

	#############
	# SETUP GPG #
	#############

	# prepare our ephemeral gnupg home dir so we can verify the signature of our
	# checksum file after download and before "install"
	if os.path.exists( GNUPGHOME ):
		shutil.rmtree( GNUPGHOME )
	os.makedirs( GNUPGHOME, mode=0o700 )
	os.chmod( GNUPGHOME, mode=0o0700 )

	# get the contents of the KEYS file shipped with our software
	try:
		with open( os.path.join(APP_DIR, 'KEYS'), 'r' ) as fd:
			KEYS = fd.read()
	except:
		# fall-back to one dir up if we're executing from 'src/'
		with open( os.path.join( os.path.split(APP_DIR)[0], 'KEYS'), 'r' ) as fd:
			KEYS = fd.read()

	gpg = gnupg.GPG( gnupghome=GNUPGHOME )
	gpg.import_keys( KEYS )

	############################
	# DETERMINE LATEST VERSION #
	############################

	metadata_filepath = os.path.join( CACHE_DIR, 'meta.json' )
	signature_filepath = os.path.join( CACHE_DIR, 'meta.json.asc' )

	# loop through each of our mirrors until we get one that's online
	metadata = ''
	for mirror in UPGRADE_MIRRORS:

		# break out of loop if we've already downloaded the metadata from
		# some mirror in our list
		if os.path.exists( metadata_filepath ) \
		 and os.path.exists( signature_filepath ):
			break

		msg = "DEBUG: Checking for updates at '" +str(mirror)+ "'"
		print( msg ); logging.debug( msg )

		# try to download the metadata json file and its detached signature
		files = [ mirror, mirror + '.asc' ]
		for f in files:

			filename = f.split('/')[-1]
			filepath = os.path.join( CACHE_DIR, filename )

			try:
				with urllib.request.urlopen( f, cafile=certifi.where() ) as url, \
				 open( filepath, 'wb' ) as out_file:
	
					# the metadata definitely shouldn't be more than 1 MB
					size_bytes = int(url.info().get('content-length'))
					if size_bytes > 1048576:
						msg = "\tMetadata too big; skipping (" +str(size_bytes)+ " bytes)"
						print( msg ); logging.debug( msg )
						break
	
					shutil.copyfileobj(url, out_file)
					continue

			except Exception as e:
				msg = "\tFailed to fetch data from mirror; skipping (" +str(e)+ ")"
				print( msg ); logging.debug( msg )
				break

	# CHECK SIGNATURE OF METADATA

	msg = "\tDEBUG: Finished downloading update metadata. Checking signature."
	print( msg ); logging.debug( msg )
		
	# open the detached signature and check it with gpg
	with open( signature_filepath, 'rb' ) as fd:
		verified = gpg.verify_file( fd, metadata_filepath )

	# check that this main signature fingerprint meets our expectations
	# bail if it a key was used other than the one we require
	if verified.fingerprint != RELEASE_KEY_SUB_FINGERPRINT:
		raise RuntimeError( 'ERROR: Invalid signature fingerprint (expected '+str(RELEASE_KEY_SUB_FINGERPRINT)+' but got '+str(verified.fingerprint)+')! Please report this as a bug.' )

	# extract from our list of signatures any signatures made with exactly the
	# keys we'd expect (check the master key and the subkey fingerprints)
	sig_info = [ verified.sig_info[key] for key in verified.sig_info if verified.sig_info[key]['fingerprint'] == RELEASE_KEY_SUB_FINGERPRINT and verified.sig_info[key]['pubkey_fingerprint'] == RELEASE_KEY_FINGERPRINT ]

	# if we couldn't find a signature that matched our requirements, bail
	if sig_info == list():
		raise RuntimeError( 'ERROR: No valid signature found! Please report this as a bug.' )
	else:
		sig_info = sig_info.pop()

	# check both the list of signatures and this other one. why not?
	# bail if either is an invalid signature
	if verified.status != 'signature valid':
		raise RuntimeError( 'ERROR: No valid signature found! Please report this as a bug (' +str(sig_info)+ ').' )
	if sig_info['status'] != 'signature valid':
		raise RuntimeError( 'ERROR: No valid sig_info signature found! Please report this as a bug (' +str(sig_info)+ ').' )

	msg = "\tDEBUG: Signature is valid (" +str(sig_info)+ ")."
	print( msg ); logging.debug( msg )

	# try to load the metadata (this is done after signature so we don't load
	# something malicious that may attack the json.loads() parser)
	try:
		with open( metadata_filepath, 'r' ) as fd:
			metadata = json.loads( fd.read() ) 
	except Exception as e:
		raise RuntimeWarning( 'Unable to upgrade. Could not fetch metadata file (' +str(e)+ '.' )
		
	# abort if it's empty
	if metadata == '':
		raise RuntimeWarning( 'Unable to upgrade. Could not fetch metadata contents.' )

	###########################
	# DOWNLOAD LATEST VERSION #
	###########################

	# TODO remove this
	BUSKILL_VERSION['SOURCE_DATE_EPOCH'] = '1598128933'

	# check metadata to see if there's a newer version than what we're running
	# note we use SOURCE_DATE_EPOCH to make version comparisons easy
	latestReleaseTime = int(metadata['latest']['buskill-app']['stable'])
	currentReleaseTime = int(BUSKILL_VERSION['SOURCE_DATE_EPOCH'])

	msg = "DEBUG: Current version: " +str(currentReleaseTime)+ ".\n"
	msg += "DEBUG: Latest version: " +str(latestReleaseTime)+ "."
	print( msg ); logging.debug( msg )

	if latestReleaseTime < currentReleaseTime:
		msg = "INFO: Current version is latest version. No new updates available."
		print( msg ); logging.info( msg )
		return 1

	# TODO: remove me
	print(metadata)

	# currently we only support x86_64 builds..
	arch = 'x86_64'

	sha256sums_urls = metadata['updates']['buskill-app'][str(latestReleaseTime)]['SHA256SUMS']
	sha256sums_filepath = os.path.join( CACHE_DIR, 'SHA256SUMS' )

	signature_urls = metadata['updates']['buskill-app'][str(latestReleaseTime)]['SHA256SUMS.asc']
	signature_filepath = os.path.join( CACHE_DIR, 'SHA256SUMS.asc' )

	archive_urls = metadata['updates']['buskill-app'][str(latestReleaseTime)][os_name_short][arch]['archive']['url']
	archive_filename = archive_urls[0].split('/')[-1]
	archive_filepath = os.path.join( CACHE_DIR, archive_filename )

	# TODO: remove me
	archive_urls.append( 'example.com/example.tar.gz' )
	sha256sums_urls.append( 'example.com/SHA256SUMS' )
	signature_urls.append( 'example.com/SHA256SUMS.asc' )

	# TODO: remove me
	print( '--------------------------------------' )
	print( 'arhcive_url:|' +str(archive_urls)+ '|' )
	print( 'sha256sum_url:|' +str(sha256sums_urls)+ '|' )
	print( 'signature_url:|' +str(signature_urls)+ '|' )

	# shuffle all three URLs but shuffle them the same
	start_state = random.getstate()
	random.shuffle( archive_urls )
	random.setstate( start_state)
	random.shuffle( sha256sums_urls )
	random.setstate( start_state)
	random.shuffle( signature_urls )
	random.setstate( start_state)

	# TODO: remove me
	print( '--------------------------------------' )
	print( 'arhcive_url:|' +str(archive_urls)+ '|' )
	print( 'sha256sum_url:|' +str(sha256sums_urls)+ '|' )
	print( 'signature_url:|' +str(signature_urls)+ '|' )

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
			print( msg ); logging.debug( msg )

			filename = download.split('/')[-1]
			filepath = os.path.join( CACHE_DIR, filename )

			try:
				with urllib.request.urlopen( download, cafile=certifi.where() ) as url, \
				 open( filepath, 'wb' ) as out_file:
	
					# don't download any files >200 MB
					size_bytes = int(url.info().get('content-length'))
					if size_bytes > 209715200:
						msg = "\tFile too big; skipping (" +str(size_bytes)+ " bytes)"
						print( msg ); logging.debug( msg )
						continue
	
					shutil.copyfileobj(url, out_file)
					msg = "\tDone"
					print( msg ); logging.debug( msg )
					break

			except Exception as e:
				msg = "\tFailed to download update; skipping (" +str(e)+ ")"
				print( msg ); logging.debug( msg )
				continue

	# CHECK SIGNATURE OF RELEASE FILES

	msg = "DEBUG: Finished downloading update files. Checking signature."
	print( msg ); logging.debug( msg )
		
	# TODO remove next 2 lines
	print( 'payload sig filepath:|' +str(signature_filepath)+ '|' )
	print( 'payload:|' +str(sha256sums_filepath)+ '|' )

	# open the detached signature and check it with gpg
	with open( signature_filepath, 'rb' ) as fd:
		verified = gpg.verify_file( fd, sha256sums_filepath )

	# check that this main signature fingerprint meets our expectations
	# bail if it a key was used other than the one we require
	if verified.fingerprint != RELEASE_KEY_SUB_FINGERPRINT:
		raise RuntimeError( 'ERROR: Invalid signature fingerprint (expected '+str(RELEASE_KEY_SUB_FINGERPRINT)+' but got '+str(verified.fingerprint)+')! Please report this as a bug.' )

	# extract from our list of signatures any signatures made with exactly the
	# keys we'd expect (check the master key and the subkey fingerprints)
	sig_info = [ verified.sig_info[key] for key in verified.sig_info if verified.sig_info[key]['fingerprint'] == RELEASE_KEY_SUB_FINGERPRINT and verified.sig_info[key]['pubkey_fingerprint'] == RELEASE_KEY_FINGERPRINT ]

	# if we couldn't find a signature that matched our requirements, bail
	if sig_info == list():
		raise RuntimeError( 'ERROR: No valid signature found! Please report this as a bug.' )
	else:
		sig_info = sig_info.pop()

	# check both the list of signatures and this other one. why not?
	# bail if either is an invalid signature
	if verified.status != 'signature valid':
		raise RuntimeError( 'ERROR: No valid signature found! Please report this as a bug (' +str(sig_info)+ ').' )
	if sig_info['status'] != 'signature valid':
		raise RuntimeError( 'ERROR: No valid sig_info signature found! Please report this as a bug (' +str(sig_info)+ ').' )

	msg = "DEBUG: Signature is valid (" +str(sig_info)+ ")."
	print( msg ); logging.debug( msg )

	print( "TODO: validate integrity, and install" )
	sys.exit(1)

	with urllib.request.urlopen( sha256sum_url, cafile=certifi.where() ) as url, \
	 open( signature_filepath, 'wb' ) as out_file:
		#sha256sum_data = url.read().decode()
		shutil.copyfileobj(url, out_file)

	# TODO: check the size of the downloads and refuse if it's something huge
	with urllib.request.urlopen( signature_url, cafile=certifi.where() ) as url, \
	 open( sha256sum_filepath, 'wb' ) as out_file:
		#signature_data = url.read().decode()
		shutil.copyfileobj(url, out_file)

	# TODO: check the size of the downloads and refuse if it's something huge
	with urllib.request.urlopen( archive_url, cafile=certifi.where() ) as url, \
	 open( archive_filepath, 'wb' ) as out_file:
		shutil.copyfileobj(url, out_file)

	####################
	# VERIFY SIGNATURE #
	####################

	with open( sha256sum_filepath, 'rb' ) as fd:
		verified = gpg.verify_file( fd, signature_filepath )

	# TODO: check if signature of our digest file is valid. if not, delete all downloads and abort with critical error

	# TODO: check if download's checksum matches our signed/verified digest file. If not, delete all downloads and abort with critical error

	####################
	# VERIFY INTEGRITY #
	####################

	# TODO verify that the downloaded archive's digest matches what's specified of the now-trustworthy SHA256SUMS file. If not, delete all downloads and abort with critical error

	###########
	# INSTALL #
	###########

	# TODO: move the new version out of cache into our EXE_DIR

	# TODO: move our current version into some old dir

	#print( sha256sum_data )
	#print( signature_data )

	#print(data)

	# TODO: determine if the latest version is newer than our current version
