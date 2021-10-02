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
# Updated: 2020-10-02
# Version: 0.1
################################################################################

################################################################################
#                                  SETTINGS                                    #
################################################################################

# n/a
WGET='/usr/bin/wget --continue --no-verbose'
UNZIP='/usr/bin/unzip -q'
P7Z='/usr/bin/7z'
TAR='/bin/tar'

################################################################################
#                                 MAIN BODY                                    #
################################################################################

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

###################
# INSTALL DEPENDS #
###################

${SUDO} rm -rf /var/lib/apt/lists/*
${SUDO} apt-get clean
${SUDO} apt-get update -o Acquire::CompressionTypes::Order::=gz || exit 1
#${SUDO} apt-get update || exit 1
${SUDO} apt-get -y install git wget gnupg unzip bzip2 p7zip-full

###################################
# DOWNLOAD LATEST STABLE RELEASES #
###################################

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
mkdir -p dist/usbRoot/sigs
pushd dist/usbRoot/sigs
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
unzip "${win_release_filename}"
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

# windows shortcut file
pushd dist/usbRoot/buskill-Windows
win_exe_file_path=`find . -type f -name buskill.exe | head -n1 2>/dev/null`
ln -s "${win_exe_file_path}" .
popd

###########
# AUTORUN #
###########

# TODO: Windows autorun script

#############################
# CREATE COMPRESSED ARCHIVE #
#############################

pushd dist

# note this must be extracted with `7z x` and not `7z e`
${P7Z} a "buskill_usbRoot_${latest_version}.7z" usbRoot/

##################
# CLEANUP & EXIT #
##################

# make sure the resulting dist/ dir permissions let subsequent CI steps upload
# the build's artifacts
chown -R ${SUDO_USER} dist

exit 0
