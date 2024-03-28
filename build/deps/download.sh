#!/bin/bash
set -x
################################################################################
# File:    build/deps/download.sh
# Purpose: Use this script to download the files in this dir. Useful if, for
#          example, you don't trust their integrity and/or want to verify them.
#
#          * https://github.com/BusKill/buskill-app/issues/2
#
# Note:    This script was built to be run in Debian or TAILS
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-07-08
# Updated: 2024-03-15
# Version: 0.2
################################################################################

sudo apt-get -y install python3-pip python3-setuptools

CURL="/usr/bin/curl"
WGET="/usr/bin/wget --retry-on-host-error --retry-connrefused"
PYTHON="/usr/bin/python3"

# in tails, we must torify
if [[ "`whoami`" == "amnesia" ]]; then
	CURL="/usr/bin/torify ${CURL}"
	WGET="/usr/bin/torify ${WGET}"
	PYTHON="/usr/bin/torify ${PYTHON}"
fi

tmpDir=`mktemp -d`
pushd "${tmpDir}"

# first get some info about our internet connection
${CURL} -s https://ifconfig.co/country | head -n1
${CURL} -s https://check.torproject.org | grep Congratulations | head -n1

# and today's date
date -u +"%Y-%m-%d"

# first download and upgrade pip (required to get some wheels)
${PYTHON} -m pip download --no-cache-dir pip==24.0
${PYTHON} -m pip install --upgrade pip==24.0

# pip (all platforms)
${PYTHON} -m pip download --no-cache-dir kivy==2.3.0 pyinstaller==6.5.0 altgraph==0.17.4 macholib==1.16.3 future==1.0.0 pefile==2023.2.7 pywin32-ctypes==0.2.2 setuptools==69.1.1 wheel==0.42.0 virtualenv==20.25.1

# pip (platform-specific binaries/wheels)
${WGET} `${CURL} -s https://pypi.org/simple/kivy/ | grep -oE 'https://.*Kivy-2.30-cp312-cp312-win_amd64.whl#'`
${WGET} `${CURL} -s https://pypi.org/simple/kivy/ | grep -oE 'https://.*Kivy-2.3.0-cp37-cp37m-macosx_10_9_x86_64.whl#'`
${WGET} `${CURL} -s https://pypi.org/simple/pypiwin32/ | grep -oE 'https://.*pypiwin32-223-py3-none-any.whl#'`
${WGET} `${CURL} -s https://pypi.org/simple/pywin32/ | grep -oE 'https://.*pywin32-306-cp312-cp312-win_amd64.whl#'`
${WGET} `${CURL} -s https://pypi.org/simple/kivy-deps-sdl2/ | grep -oE 'https://.*kivy_deps.sdl2-0.7.0-cp312-cp312-win_amd64.whl#'`
${WGET} `${CURL} -s https://pypi.org/simple/kivy-deps-glew/ | grep -oE 'https://.*kivy_deps.glew-0.3.1-cp312-cp312-win_amd64.whl#'`
${WGET} `${CURL} -s https://pypi.org/simple/kivy-deps-angle/ | grep -oE 'https://.*kivy_deps.angle-0.4.0-cp312-cp312-win_amd64.whl#'`

# misc linux
${WGET} https://github.com/niess/python-appimage/releases/download/python3.12/python3.12.2-cp312-cp312-manylinux2014_x86_64.AppImage
${WGET} https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage
${WGET} --output-document=squashfs4.4.tar.gz https://sourceforge.net/projects/squashfs/files/squashfs/squashfs4.4/squashfs4.4.tar.gz/download

# misc windows
${WGET} https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe
${WGET} https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe.asc

# misc macos
${WGET} https://github.com/libusb/libusb/releases/download/v1.0.27/libusb-1.0.27.tar.bz2
${WGET} https://github.com/libusb/libusb/releases/download/v1.0.27/libusb-1.0.27.tar.bz2.asc

# TODO: figure out how to download from GitHub Packages since Homebrew migrated
# away from bintray
# * https://github.com/BusKill/buskill-app/issues/78#issuecomment-1987360762
# * https://github.com/orgs/Homebrew/discussions/691
# * https://apple.stackexchange.com/questions/470937/how-to-get-the-url-to-download-a-homebrew-bottle
# * https://stackoverflow.com/questions/78164818/how-to-download-a-file-from-github-container-registry-cli-command-github-packa

#${WGET} https://homebrew.bintray.com/bottles/wget-1.20.3_2.catalina.bottle.tar.gz
#${WGET} https://homebrew.bintray.com/bottles/python-3.7.8.catalina.bottle.tar.gz
#${WGET} https://homebrew.bintray.com/bottles/sdl2-2.0.12_1.catalina.bottle.tar.gz
#${WGET} https://homebrew.bintray.com/bottles/sdl2_image-2.0.5.catalina.bottle.tar.gz
#${WGET} https://homebrew.bintray.com/bottles/sdl2_ttf-2.0.15.catalina.bottle.tar.gz
#${WGET} https://homebrew.bintray.com/bottles/sdl2_mixer-2.0.4.catalina.bottle.tar.gz
#${WGET} https://homebrew.bintray.com/bottles/libmodplug-0.8.9.0.catalina.bottle.1.tar.gz

# get checksums
sha256sum *
