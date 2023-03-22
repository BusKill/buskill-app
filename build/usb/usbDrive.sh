#!/bin/bash
set -x
################################################################################
# File:    usbDrive.sh
# Purpose: Script that prepares an archive of the files that should be put on
#          the cross-platform, UX-friendly BusKill USB drive. See also
#
#          * https://github.com/BusKill/buskill-app/issues/22
#
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-10-02
# Updated: 2020-10-03
# Version: 0.2
################################################################################

################################################################################
#                                  SETTINGS                                    #
################################################################################

# paths
ECHO="`which echo`"
GREP="`which grep`"
APT_GET="`which apt-get`"
SUDO="`which sudo`"

USB_ROOT_PATH='dist/usbRoot'
SIGS_PATH="${USB_ROOT_PATH}/sigs"

################################################################################
#                                 MAIN BODY                                    #
################################################################################

###########
# CONFIRM #
###########

# for safety, exit if this script is executed without a '--yes' argument
${ECHO} "${@}" | ${GREP} '\--yes' &> /dev/null
if [ $? -ne 0 ]; then
  ${ECHO} "WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING"
  ${ECHO} "================================================================================"
  ${ECHO} "WARNING: THIS SCRIPT WAS DESIGNED TO RUN INSIDE AN EPHEMERAL DOCKER CONTAINER."
  ${ECHO} "         IT MAY ALTER OR DAMANGE YOUR SYSTEM IF RUN OUTSIDE A DOCKER CONTAINER!"
  ${ECHO} "================================================================================"
  ${ECHO} "WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING"
  ${ECHO}
  ${ECHO} "Cowardly refusing to execute without the '--yes' argument for your protection. If really you want to proceed with damaging your system, retry with the '--yes' argument"
  ${ECHO}
  ${ECHO} "You can run this script inside a docker container by executing this instead:"
  ${ECHO}
  ${ECHO} "  build/usb/debianWrapper.sh"
  ${ECHO} "  ^^^^^^^^^^^^^^^^^^^^^^^^^^"
  exit 1
fi

# this script isn't robust enough
if [ ! -e "`pwd`/build/usb/usbDrive.sh" ]; then
	echo "ERROR: This script should only be executed from the root of the github dir."
	exit 1
fi

# re-run this as root if we're not already (needed for docker host stuff)
if [[ `whoami` != "root" ]]; then
        sudo ./build/usb/usbDrive.sh || exit $?

        # this exits the parent process run by the user
        exit 0
fi

####################
# CLEANUP LAST RUN #
####################

${SUDO} rm -rf "${USB_ROOT_PATH}.old"
${SUDO} mv "${USB_ROOT_PATH}" "${USB_ROOT_PATH}.old"
mkdir -p "${USB_ROOT_PATH}"

###################
# INSTALL DEPENDS #
###################

${SUDO} rm -rf /var/lib/apt/lists/*
${SUDO} ${APT_GET} clean
${SUDO} ${APT_GET} update -o Acquire::CompressionTypes::Order::=gz || exit 1
#${SUDO} ${APT_GET} update || exit 1
#${SUDO} ${APT_GET} -y install git wget gnupg unzip rar bzip2 p7zip-full
${SUDO} ${APT_GET} -y install git wget gnupg zip unzip bzip2 p7zip-full

# get absolute paths of newly-installed commands and set args
WGET="`which wget` --continue --no-verbose"
ZIP="`which zip` --quiet"
UNZIP="`which unzip` -q"
P7Z="`which 7z`"
#RAR=`which rar`"
TAR="`which tar`"

###################################
# DOWNLOAD LATEST STABLE RELEASES #
###################################

# prevent "detected dubious ownership in repository" error
pwd
git config --global --add safe.directory .
git config --global --add safe.directory /root/buskill-app

# get the latest version tag
latest_version=`git tag | grep -iE '^v[0-9]*\.[0-9]*' | tail -n1`

# determine the filename of all our releases
lin_release_filename="buskill-lin-${latest_version}-x86_64.tbz"
win_release_filename="buskill-win-${latest_version}-x86_64.zip"
mac_release_filename="buskill-mac-${latest_version}-x86_64.dmg"

# and the dir to which the release archives will extract
lin_release_dir="buskill-lin-${latest_version}-x86_64"
win_release_dir="buskill-win-${latest_version}-x86_64"

# determine the URL to download each of our releases
release_url_prefix="https://github.com/BusKill/buskill-app/releases/download/${latest_version}"
lin_release_url="${release_url_prefix}/${lin_release_filename}"
win_release_url="${release_url_prefix}/${win_release_filename}"
mac_release_url="${release_url_prefix}/${mac_release_filename}"

# download releases
mkdir -p "${SIGS_PATH}"
pushd "${SIGS_PATH}"
${WGET} "${lin_release_url}"
${WGET} "${win_release_url}"
${WGET} "${mac_release_url}"

# download checksum & checksum signature
${WGET} "${release_url_prefix}/SHA256SUMS"
${WGET} "${release_url_prefix}/SHA256SUMS.asc"

############################
# CHECK RELEASE SIGNATURES #
############################

cp ../../../KEYS .

# setup gpg keyring "homedir"
mkdir -p .gnupg
chmod 0700 .gnupg
gpg --homedir ".gnupg" --import "KEYS"

gpgv --homedir ".gnupg" --keyring ".gnupg/pubring.kbx" "SHA256SUMS.asc" SHA256SUMS

# confirm that the signature is valid. `gpgv` would exit 2 if the signature
# isn't in our keyring (so we are effectively pinning it), it exits 1 if there's
# any BAD signatures, and exits 0 "if everything is fine"
if [[ $? -ne 0 ]]; then
	echo "ERROR: Invalid PGP signature on SHA256SUMS digest!"
	exit 1
fi

# confirm that the files all have the same checksum as our signed digest file
sha256sum -c SHA256SUMS
if [[ $? -ne 0 ]]; then
	echo "ERROR: Invalid checksum!"
	exit 1
fi

########################
# PREPARE RELEASE DIRS #
########################

# extract the now-verified release archives to OS-specific directories that
# are super-easy to use for users without additional steps

# windows
${UNZIP} "${win_release_filename}"
mv "${win_release_dir}" ../buskill-Windows

# linux
${TAR} -xjf "${lin_release_filename}"
mv "${lin_release_dir}" ../buskill-Linux

# MacOS
mkdir ../buskill-MacOS
cp "${mac_release_filename}" ../buskill-MacOS/

popd

###################
# CREATE SYMLINKS #
###################

# create symlinks to executables to create an easy UX
pushd ${USB_ROOT_PATH}

# windows shortcut file
# 2022-05: This works for .zip files created in Linux and extracted in Linux.
#          This does not work for .zip files created in Linux and extracted in
#          Windows.
#            * https://github.com/BusKill/buskill-app/issues/22
#pushd dist/usbRoot/buskill-Windows
#win_exe_file_path=`find . -type f -name buskill.exe | head -n1 2>/dev/null`
#ln -s "${win_exe_file_path}" .
#popd

# shortcuts are very important for Windows users' UX
# since we can't create shortcuts and store them in the archive, we create a
# simple script that can be double-clicked to create the shortcut directly on
# the USB drive after the files are copied to the USB drive.

# It's not easy to create shortcuts in Windows CLI
# * https://superuser.com/a/455383/551559

cat >> provision.bat <<EOF
@echo off

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: File:    provision.bat
:: Version: 0.1
:: Purpose: Preforms final step (which can't be done otherwise) when
::          initializing the USB Storage Drive for BusKill. For more info, see:
::           * https://github.com/BusKill/buskill-app/issues/22
::           * https://docs.buskill.in/buskill-app/en/dev/hardware_dev/storage.html
:: Authors: Michael Altfield <michael@michaelaltfield.net>
:: Created: 2022-05-03
:: Updated: 2022-05-03
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::
:: CREATE SHORTCUTS ::
::::::::::::::::::::::

:: shortcuts (as opposed to symlinks) in Windows can't be created in with a
:: simple PowerShell or cmd command. Rather, we have to awkwardly create this
:: visual basic script, execute it, then delete it :/
::  * https://superuser.com/a/455383/551559
set TMP_SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"
set USB_ROOT_PATH=%~dp0

echo Set oWS = WScript.CreateObject("WScript.Shell") >> %TMP_SCRIPT%
echo sLinkFile = "%USB_ROOT_PATH%\buskill-Windows\buskill.lnk" >> %TMP_SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %TMP_SCRIPT%
echo oLink.TargetPath = "%USB_ROOT_PATH%\buskill-Windows\buskill-${latest_version}-x86_64\buskill.exe" >> %TMP_SCRIPT%
echo oLink.Save >> %TMP_SCRIPT%

cscript /nologo %TMP_SCRIPT%
del %TMP_SCRIPT%

::::::::::::::::::::::::::
:: FILE INTEGRITY CHECK ::
::::::::::::::::::::::::::

:: TODO: Check all the files on the disk to make sure they match SHA256SUMS
::       ...or at least count the number of files with
::          dir /b * /s | find /c /v ""

::::::::::::::::::
:: HUMAN OUTPUT ::
::::::::::::::::::

echo INFO: PASS or FAIL?
echo:
echo INFO: PASS. PASS. PASS. PASS. PASS. PASS. PASS. PASS. PASS
echo INFO: PASS. USB Storage Drive Initialized Successfully.

::::::::::::::::
:: CLEAN EXIT ::
::::::::::::::::

:: commit suicide (delete this script)
:: leave the command window open so the human can read the output
del %0 & pause
EOF

popd

###########
# AUTORUN #
###########

pushd ${USB_ROOT_PATH}

# Windows autorun file
# 2022-05: I couldn't get this to work. Is it still a thing in Windows 10?
#cat >> Autorun.inf <<EOF
#[AutoRun]
#OPEN=buskill-Windows/buskill.exe
#ICON=buskill-Windows/buskill.exe
#ACTION=Start my application
#LABEL=BusKill
#EOF

# Human-Readable README file
cat >> README.txt <<EOF
Thank you for purchasing a BusKill cable!

The software included on this USB drive must be installed on your computer in
order to function. For instructions on how to get started using your BusKill
cable, please visit:

 * https://buskill.in/start
EOF

# checksum
# Note: This MUST be the very last file to be created!
sha256sum `find . -type f` > SHA256SUMS

popd

#############################
# CREATE COMPRESSED ARCHIVE #
#############################

pushd dist

# cleanup old compressed archives
rm -f "buskill_usbRoot_${latest_version}.7z"
rm -f "buskill_usbRoot_${latest_version}.zip"
rm -f "buskill_usbRoot_${latest_version}.tbz"

# note this must be extracted with `7z x` and not `7z e`
# note also we use 7zip instead of tarballs or .zip because .7z files support
# symlinks and are very cross-platform
${P7Z} a "buskill_usbRoot_${latest_version}.7z" usbRoot/

${ZIP} --symlinks --recurse-paths "buskill_usbRoot_${latest_version}.zip" usbRoot/

${TAR} -cjf "buskill_usbRoot_${latest_version}.tbz" usbRoot/

#${RAR} a "buskill_usbRoot_${latest_version}.rar" usbRoot/

##################
# CLEANUP & EXIT #
##################

# make sure the resulting dist/ dir permissions let subsequent CI steps upload
# the build's artifacts
if [[ ${SUDO_USER} ]]; then
	chown -R ${SUDO_USER} dist
fi

exit 0
