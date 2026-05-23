#!/usr/bin/env python3
"""
::

  File:    packages/buskill/root_child_win.py
  Authors: Michael Altfield <michael@buskill.in>
  Created: 2025-05-23
  Updated: 2025-05-23
  Version: 0.1

  WARNING: THIS IS EXPERIMENTAL SOFTWARE THAT IS DESIGNED TO DESTROY DATA.

This is a very small python script that is intended to be run with Administrator privileges on Windows platforms. It should be as small and paranoid as possible, and only contain logic that cannot run as the normal user due to insufficient permissions (eg shutting down the machine, wiping VeraCrypt volume headers)

For more info, see: https://buskill.in/

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

################################################################################
#                                   IMPORTS                                    #
################################################################################

import logging, re, sys, subprocess, os, secrets, platform, ctypes

################################################################################
#                                  SETTINGS                                    #
################################################################################

VERACRYPT_HEADER_SIZE = 131072  # 128 KB
WIPE_PASSES = 3

# common VeraCrypt installation paths on Windows
VERACRYPT_SEARCH_PATHS = [
	os.path.join( os.environ.get('ProgramFiles', 'C:\\Program Files'), 'VeraCrypt', 'VeraCrypt.exe' ),
	os.path.join( os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'VeraCrypt', 'VeraCrypt.exe' ),
	os.path.join( os.environ.get('ProgramW6432', 'C:\\Program Files'), 'VeraCrypt', 'VeraCrypt.exe' ),
	'C:\\Program Files\\VeraCrypt\\VeraCrypt.exe',
	'C:\\Program Files (x86)\\VeraCrypt\\VeraCrypt.exe',
]

################################################################################
#                                  FUNCTIONS                                   #
################################################################################

# locate the VeraCrypt.exe binary on the system
def find_veracrypt_exe():

	msg = "Searching for VeraCrypt.exe installation"
	logging.info(msg)

	for candidate_path in VERACRYPT_SEARCH_PATHS:

		msg = "Checking VeraCrypt path: '" +str(candidate_path)+ "'"
		logging.debug(msg)

		# paranoid: reject symlinks to prevent redirection attacks
		if os.path.islink( candidate_path ):
			msg = "Rejected symlink at '" +str(candidate_path)+ "'"
			logging.warning(msg)
			continue

		if os.path.isfile( candidate_path ):
			msg = "Found VeraCrypt.exe at '" +str(candidate_path)+ "'"
			logging.info(msg)
			return candidate_path

	msg = "VeraCrypt.exe not found in any standard location!"
	logging.error(msg)
	return None

# find all currently mounted VeraCrypt volumes
def find_veracrypt_volumes():

	msg = "Attempting to find mounted VeraCrypt volumes"
	logging.info(msg)

	veracrypt_exe = find_veracrypt_exe()
	if veracrypt_exe is None:
		msg = "Cannot list volumes: VeraCrypt.exe not found"
		logging.error(msg)
		return []

	volumes = []

	try:
		msg = "Attempting to execute '" +str(veracrypt_exe)+ " /list'"
		logging.info(msg)

		result = subprocess.run(
		 [ veracrypt_exe, '/list' ],
		 capture_output=True,
		 text=True,
		 timeout=30
		)

		msg = "subprocess returncode|" +str(result.returncode)+ "|"
		logging.debug(msg)

		msg = "subprocess stdout|" +str(result.stdout)+ "|"
		logging.debug(msg)

		msg = "subprocess stderr|" +str(result.stderr)+ "|"
		logging.debug(msg)

		# parse each line of the output
		# typical format: "1: \??\Volume{GUID}\ X: \?\device\path"
		# or: "1: C:\path\to\container.hc X: -"
		output = result.stdout + result.stderr

		for line in output.splitlines():

			line = line.strip()
			if not line:
				continue

			msg = "Parsing volume list line: '" +str(line)+ "'"
			logging.debug(msg)

			# try to match lines like:
			#   "1: \??\Volume{...}\  D:  ..."
			#   "1: C:\path\to\file.hc  D:  ..."
			# the format is: <slot>: <volume_path> <drive_letter>: ...
			match = re.match(
			 r'^(\d+):\s+(.+?)\s+([A-Za-z]):',
			 line
			)

			if match:
				slot_num = match.group(1)
				volume_path = match.group(2).strip()
				drive_letter = match.group(3).upper()

				msg = "Found mounted VeraCrypt volume: slot=" +str(slot_num)+ " volume_path='" +str(volume_path)+ "' drive_letter='" +str(drive_letter)+ ":'"
				logging.info(msg)

				volumes.append({
				 'drive_letter': drive_letter,
				 'volume_path': volume_path,
				})
			else:
				msg = "Could not parse volume list line: '" +str(line)+ "'"
				logging.debug(msg)

	except subprocess.TimeoutExpired:
		msg = "Timed out waiting for VeraCrypt /list"
		logging.error(msg)

	except Exception as e:
		msg = "Failed to list VeraCrypt volumes! " +str(e)
		logging.error(msg)

	msg = "Found " +str(len(volumes))+ " mounted VeraCrypt volume(s)"
	logging.info(msg)

	return volumes

# wipe the VeraCrypt headers of a volume to make it permanently inaccessible
def wipe_veracrypt_headers( volume_path ):

	msg = "Attempting to wipe VeraCrypt headers for volume: '" +str(volume_path)+ "'"
	logging.info(msg)

	# paranoid: validate volume_path is not empty
	if not volume_path or not volume_path.strip():
		msg = "volume_path is empty! Refusing to wipe."
		logging.error(msg)
		return False

	# paranoid: reject symlinks
	if os.path.islink( volume_path ):
		msg = "volume_path is a symlink! Refusing to wipe: '" +str(volume_path)+ "'"
		logging.error(msg)
		return False

	# determine if this is a file container or a raw partition/disk
	is_raw_device = False
	if volume_path.startswith( '\\\\.\\' ) or volume_path.startswith( '\\\\?\\' ) or volume_path.startswith( '\\??\\' ):
		is_raw_device = True
		msg = "Volume appears to be a raw device/partition: '" +str(volume_path)+ "'"
		logging.info(msg)
	else:
		msg = "Volume appears to be a file container: '" +str(volume_path)+ "'"
		logging.info(msg)

	try:
		if is_raw_device:
			# for raw devices, we need to use Win32 API via ctypes
			_wipe_raw_device_headers( volume_path )
		else:
			# for file containers, use standard file I/O
			_wipe_file_container_headers( volume_path )

		msg = "Successfully wiped VeraCrypt headers for volume: '" +str(volume_path)+ "'"
		logging.info(msg)
		return True

	except Exception as e:
		msg = "Failed to wipe VeraCrypt headers for volume '" +str(volume_path)+ "': " +str(e)
		logging.error(msg)
		return False

# wipe headers of a file-based VeraCrypt container
def _wipe_file_container_headers( file_path ):

	msg = "Wiping file container headers: '" +str(file_path)+ "'"
	logging.info(msg)

	# paranoid: verify path exists and is a regular file
	if not os.path.isfile( file_path ):
		msg = "File does not exist or is not a regular file: '" +str(file_path)+ "'"
		logging.error(msg)
		raise FileNotFoundError( msg )

	file_size = os.path.getsize( file_path )
	msg = "File size: " +str(file_size)+ " bytes"
	logging.debug(msg)

	if file_size < VERACRYPT_HEADER_SIZE * 2:
		msg = "File is too small to contain VeraCrypt headers (" +str(file_size)+ " bytes). Refusing to wipe."
		logging.error(msg)
		raise ValueError( msg )

	backup_header_offset = file_size - VERACRYPT_HEADER_SIZE

	for pass_num in range( 1, WIPE_PASSES + 1 ):

		msg = "Wipe pass " +str(pass_num)+ " of " +str(WIPE_PASSES)+ " for file container: '" +str(file_path)+ "'"
		logging.info(msg)

		# generate cryptographically secure random data for this pass
		random_data_front = secrets.token_bytes( VERACRYPT_HEADER_SIZE )
		random_data_back = secrets.token_bytes( VERACRYPT_HEADER_SIZE )

		with open( file_path, 'r+b' ) as f:

			# wipe the primary header at offset 0
			msg = "Overwriting primary header (offset 0, " +str(VERACRYPT_HEADER_SIZE)+ " bytes), pass " +str(pass_num)
			logging.debug(msg)

			f.seek( 0 )
			f.write( random_data_front )
			f.flush()
			os.fsync( f.fileno() )

			# wipe the backup header at the end of the file
			msg = "Overwriting backup header (offset " +str(backup_header_offset)+ ", " +str(VERACRYPT_HEADER_SIZE)+ " bytes), pass " +str(pass_num)
			logging.debug(msg)

			f.seek( backup_header_offset )
			f.write( random_data_back )
			f.flush()
			os.fsync( f.fileno() )

		msg = "Wipe pass " +str(pass_num)+ " complete for: '" +str(file_path)+ "'"
		logging.info(msg)

	msg = "All " +str(WIPE_PASSES)+ " wipe passes complete for file container: '" +str(file_path)+ "'"
	logging.info(msg)

# wipe headers of a raw device (partition/disk) VeraCrypt volume
def _wipe_raw_device_headers( device_path ):

	msg = "Wiping raw device headers: '" +str(device_path)+ "'"
	logging.info(msg)

	# normalize device path for CreateFileW
	# VeraCrypt may report paths like \??\Volume{GUID}\ — normalize to \\?\
	normalized_path = device_path
	if normalized_path.startswith( '\\??\\'  ):
		normalized_path = '\\\\?\\' + normalized_path[4:]

	msg = "Normalized device path: '" +str(normalized_path)+ "'"
	logging.debug(msg)

	try:
		# use Win32 CreateFileW to open the raw device
		GENERIC_READ = 0x80000000
		GENERIC_WRITE = 0x40000000
		FILE_SHARE_READ = 0x00000001
		FILE_SHARE_WRITE = 0x00000002
		OPEN_EXISTING = 3
		FILE_FLAG_WRITE_THROUGH = 0x80000000
		FILE_FLAG_NO_BUFFERING = 0x20000000
		INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

		kernel32 = ctypes.windll.kernel32

		handle = kernel32.CreateFileW(
		 normalized_path,
		 GENERIC_READ | GENERIC_WRITE,
		 FILE_SHARE_READ | FILE_SHARE_WRITE,
		 None,
		 OPEN_EXISTING,
		 FILE_FLAG_WRITE_THROUGH,
		 None
		)

		if handle == INVALID_HANDLE_VALUE:
			error_code = ctypes.GetLastError()
			msg = "Failed to open raw device '" +str(normalized_path)+ "': Windows error code " +str(error_code)
			logging.error(msg)
			raise OSError( msg )

		msg = "Opened raw device handle for: '" +str(normalized_path)+ "'"
		logging.debug(msg)

		try:
			# get the device size using DeviceIoControl IOCTL_DISK_GET_LENGTH_INFO
			IOCTL_DISK_GET_LENGTH_INFO = 0x0007405C

			class DISK_LENGTH_INFO(ctypes.Structure):
				_fields_ = [("Length", ctypes.c_longlong)]

			length_info = DISK_LENGTH_INFO()
			bytes_returned = ctypes.c_ulong(0)

			success = kernel32.DeviceIoControl(
			 handle,
			 IOCTL_DISK_GET_LENGTH_INFO,
			 None,
			 0,
			 ctypes.byref(length_info),
			 ctypes.sizeof(length_info),
			 ctypes.byref(bytes_returned),
			 None
			)

			if not success:
				error_code = ctypes.GetLastError()
				msg = "Failed to get device size for '" +str(normalized_path)+ "': Windows error code " +str(error_code)
				logging.error(msg)
				raise OSError( msg )

			device_size = length_info.Length
			msg = "Device size: " +str(device_size)+ " bytes"
			logging.debug(msg)

			if device_size < VERACRYPT_HEADER_SIZE * 2:
				msg = "Device is too small to contain VeraCrypt headers (" +str(device_size)+ " bytes). Refusing to wipe."
				logging.error(msg)
				raise ValueError( msg )

			backup_header_offset = device_size - VERACRYPT_HEADER_SIZE

			for pass_num in range( 1, WIPE_PASSES + 1 ):

				msg = "Wipe pass " +str(pass_num)+ " of " +str(WIPE_PASSES)+ " for raw device: '" +str(device_path)+ "'"
				logging.info(msg)

				random_data_front = secrets.token_bytes( VERACRYPT_HEADER_SIZE )
				random_data_back = secrets.token_bytes( VERACRYPT_HEADER_SIZE )

				bytes_written = ctypes.c_ulong(0)

				# seek to offset 0 and wipe primary header
				msg = "Overwriting primary header (offset 0, " +str(VERACRYPT_HEADER_SIZE)+ " bytes), pass " +str(pass_num)
				logging.debug(msg)

				kernel32.SetFilePointerEx(
				 handle,
				 ctypes.c_longlong(0),
				 None,
				 0  # FILE_BEGIN
				)

				success = kernel32.WriteFile(
				 handle,
				 random_data_front,
				 VERACRYPT_HEADER_SIZE,
				 ctypes.byref(bytes_written),
				 None
				)

				if not success:
					error_code = ctypes.GetLastError()
					msg = "Failed to write primary header, pass " +str(pass_num)+ ": Windows error code " +str(error_code)
					logging.error(msg)

				# seek to backup header offset and wipe backup header
				msg = "Overwriting backup header (offset " +str(backup_header_offset)+ ", " +str(VERACRYPT_HEADER_SIZE)+ " bytes), pass " +str(pass_num)
				logging.debug(msg)

				kernel32.SetFilePointerEx(
				 handle,
				 ctypes.c_longlong(backup_header_offset),
				 None,
				 0  # FILE_BEGIN
				)

				success = kernel32.WriteFile(
				 handle,
				 random_data_back,
				 VERACRYPT_HEADER_SIZE,
				 ctypes.byref(bytes_written),
				 None
				)

				if not success:
					error_code = ctypes.GetLastError()
					msg = "Failed to write backup header, pass " +str(pass_num)+ ": Windows error code " +str(error_code)
					logging.error(msg)

				# flush to ensure data is written to disk
				kernel32.FlushFileBuffers( handle )

				msg = "Wipe pass " +str(pass_num)+ " complete for: '" +str(device_path)+ "'"
				logging.info(msg)

			msg = "All " +str(WIPE_PASSES)+ " wipe passes complete for raw device: '" +str(device_path)+ "'"
			logging.info(msg)

		finally:
			# always close the handle
			kernel32.CloseHandle( handle )
			msg = "Closed raw device handle for: '" +str(normalized_path)+ "'"
			logging.debug(msg)

	except Exception as e:
		msg = "Exception during raw device header wipe for '" +str(device_path)+ "': " +str(e)
		logging.error(msg)
		raise

# this function will trigger the VeraCrypt self-destruct sequence on Windows
def trigger_veracrypt_selfdestruct():

	msg = "BusKill VeraCrypt self-destruct trigger executing now"
	logging.info(msg)

	veracrypt_exe = find_veracrypt_exe()
	if veracrypt_exe is None:
		msg = "Cannot execute self-destruct: VeraCrypt.exe not found!"
		logging.error(msg)
		# still attempt shutdown even if VeraCrypt is not found
		trigger_hard_shutdown()
		return

	# step 1: find all currently mounted VeraCrypt volumes before dismounting
	msg = "Step 1: Discovering mounted VeraCrypt volumes"
	logging.info(msg)

	volumes = find_veracrypt_volumes()

	# step 2: force dismount all VeraCrypt volumes
	msg = "Step 2: Force dismounting all VeraCrypt volumes"
	logging.info(msg)

	try:
		msg = "Attempting to execute '" +str(veracrypt_exe)+ " /dismount /force /quit /silent'"
		logging.info(msg)

		result = subprocess.run(
		 [ veracrypt_exe, '/dismount', '/force', '/quit', '/silent' ],
		 capture_output=True,
		 text=True,
		 timeout=60
		)

		msg = "subprocess returncode|" +str(result.returncode)+ "|"
		logging.debug(msg)

		msg = "subprocess stdout|" +str(result.stdout)+ "|"
		logging.debug(msg)

		msg = "subprocess stderr|" +str(result.stderr)+ "|"
		logging.debug(msg)

		if result.returncode != 0:
			msg = "Force dismount returned non-zero exit code: " +str(result.returncode)
			logging.warning(msg)

	except subprocess.TimeoutExpired:
		msg = "Timed out waiting for VeraCrypt dismount!"
		logging.error(msg)

	except Exception as e:
		msg = "Failed to dismount VeraCrypt volumes! " +str(e)
		logging.error(msg)

	# step 3: wipe VeraCrypt headers for each volume
	msg = "Step 3: Wiping VeraCrypt headers for " +str(len(volumes))+ " volume(s)"
	logging.info(msg)

	for volume in volumes:

		volume_path = volume.get( 'volume_path', '' )

		msg = "Wiping headers for volume: '" +str(volume_path)+ "' (was mounted at " +str(volume.get('drive_letter', '?'))+ ":)"
		logging.info(msg)

		try:
			wipe_veracrypt_headers( volume_path )
		except Exception as e:
			msg = "Failed to wipe headers for volume '" +str(volume_path)+ "': " +str(e)
			logging.error(msg)
			# continue wiping other volumes even if one fails

	# step 4: initiate hard shutdown
	msg = "Step 4: Initiating hard shutdown"
	logging.info(msg)

	trigger_hard_shutdown()

# this function will force an immediate shutdown of the Windows machine
def trigger_hard_shutdown():

	msg = "BusKill hard-shutdown trigger executing now"
	logging.info(msg)

	# first try: shutdown /s /f /t 0
	trigger_hard_shutdown_immediate()

# shutdown the computer with `shutdown /s /f /t 0`
def trigger_hard_shutdown_immediate():

	try:
		msg = "Attempting to execute `shutdown /s /f /t 0`"
		logging.info(msg)

		result = subprocess.run(
		 [ 'shutdown', '/s', '/f', '/t', '0' ],
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
			msg = "Failed to execute `shutdown /s /f /t 0`!"
			logging.warning(msg)

		trigger_hard_shutdown_poweroff()

	except Exception as e:
		# that didn't work; log it and try fallback
		msg = "Failed to execute `shutdown /s /f /t 0`! " +str(e)
		logging.warning(msg)

		trigger_hard_shutdown_poweroff()

# fallback: shutdown the computer with `shutdown /p /f`
def trigger_hard_shutdown_poweroff():

	try:
		msg = "Attempting to execute `shutdown /p /f`"
		logging.info(msg)

		result = subprocess.run(
		 [ 'shutdown', '/p', '/f' ],
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
			msg = "Failed to execute `shutdown /p /f`! "
			logging.error(msg)

	except Exception as e:
		# that didn't work; log it and give up :(
		msg = "Failed to execute `shutdown /p /f`! " +str(e)
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
# note: Windows paths include ':' for drive letters (e.g. C:\path\to\file)
if not re.match( "^[A-Za-z0-9\-\_\./\ :\\\\]+$", log_file_path ):
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
msg = "root_child_win is writing to log file '" +str(log_file_path)+ "'"
logging.info(msg)

msg = "Platform: " +str(platform.platform())
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
	if command == "veracrypt-self-destruct":
		# they want us to self-destruct VeraCrypt volumes; do it!
		msg = "Command is 'veracrypt-self-destruct'"
		logging.debug(msg)

		try:
			msg = "Attempting to call trigger_veracrypt_selfdestruct()"
			logging.debug(msg)

			trigger_veracrypt_selfdestruct()
			msg = "Finished executing 'veracrypt-self-destruct'\n"
			logging.info(msg)

		except Exception as e:
			msg = "Failed to execute trigger_veracrypt_selfdestruct()\n" +str(e)
			logging.error(msg)

	elif command == "soft-shutdown":
		# they want us to shutdown the machine; do it!
		msg = "Command is 'soft-shutdown'"
		logging.debug(msg)

		try:
			msg = "Attempting to call trigger_hard_shutdown()"
			logging.debug(msg)

			trigger_hard_shutdown()
			msg = "Finished executing 'soft-shutdown'\n"
			logging.info(msg)

		except Exception as e:
			msg = "Failed to execute trigger_hard_shutdown()\n" +str(e)
			logging.error(msg)

	else:   
		# I have no idea what they want; tell them we ignored the request
		msg = "Unknown Command Ignored\n"
		logging.warning(msg)

	sys.stdout.buffer.write( msg.encode(encoding='ascii') )
	sys.stdout.flush()
