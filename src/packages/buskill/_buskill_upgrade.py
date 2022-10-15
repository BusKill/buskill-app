#!/usr/bin/env python3.7
"""
::

  File:    packages/buskill/upgrade.py
  Authors: Michael Altfield <michael@buskill.in>
  Created: 2022-10-15
  Updated: 2022-10-15
  Version: 0.`

This file contains logic related to upgrading the BusKill app

For more info, see: https://buskill.in/
"""

################################################################################
#                                   IMPORTS                                    #
################################################################################

import os, gnupg, random, urllib.request, certifi, shutil, json, subprocess, math, re
from distutils.version import LooseVersion

import logging
logger = logging.getLogger( __name__ )

################################################################################
#                                  SETTINGS                                    #
################################################################################

UPGRADE_MIRRORS = [
 'https://raw.githubusercontent.com/BusKill/buskill-app/master/updates/v1/meta.json',
 'https://gitlab.com/buskill/buskill-app/-/raw/master/updates/v1/meta.json',
 'https://repo.buskill.in/buskill-app/v1/meta.json',
 'https://repo.michaelaltfield.net/buskill-app/v1/meta.json',
]
random.shuffle(UPGRADE_MIRRORS)

class Mixin:

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
			with open( os.path.join(self.RUNTIME_DIR, 'KEYS'), 'r' ) as fd:
				KEYS = fd.read()
		except:
			# fall-back to one dir up if we're executing from 'src/'
			with open( os.path.join( os.path.split(self.RUNTIME_DIR)[0], 'KEYS'), 'r' ) as fd:
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
		if verified.fingerprint != self.RELEASE_KEY_SUB_FINGERPRINT:
			self.wipeCache()
			msg = 'ERROR: Invalid signature fingerprint (expected '+str(self.RELEASE_KEY_SUB_FINGERPRINT)+' but got '+str(verified.fingerprint)+')! Please report this as a bug.'
			print( msg ); logger.debug( msg )
			raise RuntimeError( msg )

		# extract from our list of signatures any signatures made with exactly the
		# keys we'd expect (check the master key and the subkey fingerprints)
		sig_info = [ verified.sig_info[key] for key in verified.sig_info if verified.sig_info[key]['fingerprint'] == self.RELEASE_KEY_SUB_FINGERPRINT and verified.sig_info[key]['pubkey_fingerprint'] == self.RELEASE_KEY_FINGERPRINT ]

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
		if self.BUSKILL_VERSION['SOURCE_DATE_EPOCH'] == '':
			result = subprocess.run( [
			 'git',
			 '--git-dir=/home/user/sandbox/buskill-app/.git',
			 'log',
			 '-1',
			 '--pretty=%ct'
			], capture_output = True )
			self.BUSKILL_VERSION['SOURCE_DATE_EPOCH'] = int( result.stdout )

		# check metadata to see if there's a newer version than what we're running
		latestRelease = metadata['latest']['buskill-app']['stable']
		currentRelease = self.BUSKILL_VERSION['VERSION']

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
		if verified.fingerprint != self.RELEASE_KEY_SUB_FINGERPRINT:
			self.wipeCache()
			msg = 'ERROR: Invalid signature fingerprint (expected '+str(self.RELEASE_KEY_SUB_FINGERPRINT)+' but got '+str(verified.fingerprint)+')! Please report this as a bug.'
			print( msg ); logger.debug( msg )
			raise RuntimeError( msg )

		# extract from our list of signatures any signatures made with exactly the
		# keys we'd expect (check the master key and the subkey fingerprints)
		sig_info = [ verified.sig_info[key] for key in verified.sig_info if verified.sig_info[key]['fingerprint'] == self.RELEASE_KEY_SUB_FINGERPRINT and verified.sig_info[key]['pubkey_fingerprint'] == self.RELEASE_KEY_FINGERPRINT ]

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
