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
# Updated: 2020-07-08
# Version: 0.1
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
${PYTHON} -m pip download --no-cache-dir pip==20.1.1
${PYTHON} -m pip install --upgrade pip==20.1.1

# pip (all platforms)
${PYTHON} -m pip download --no-cache-dir kivy==1.11.1 libusb1==1.8 pyinstaller==3.6 altgraph==0.17 macholib==1.14 future==0.18.2 pefile==2019.4.18 pywin32-ctypes==0.2.0 setuptools==49.1.0 wheel==0.34.2 virtualenv==20.0.26

# pip (platform-specific binaries/wheels)
${WGET} `${CURL} -s https://pypi.org/simple/kivy/ | grep -oE 'https://.*Kivy-1.11.1-cp37-cp37m-win_amd64.whl#'`
${WGET} `${CURL} -s https://pypi.org/simple/kivy/ | grep -oE 'https://.*Kivy-1.11.1-cp37-cp37m-macosx_10_6_intel.macosx_10_9_intel.macosx_10_9_x86_64.macosx_10_10_intel.macosx_10_10_x86_64.whl#'`
${WGET} `${CURL} -s https://pypi.org/simple/pypiwin32/ | grep -oE 'https://.*pypiwin32-223-py3-none-any.whl#'`
${WGET} `${CURL} -s https://pypi.org/simple/pywin32/ | grep -oE 'https://.*pywin32-228-cp37-cp37m-win_amd64.whl#'`
${WGET} `${CURL} -s https://pypi.org/simple/kivy-deps-sdl2/ | grep -oE 'https://.*kivy_deps.sdl2-0.2.0-cp37-cp37m-win_amd64.whl#'`
${WGET} `${CURL} -s https://pypi.org/simple/kivy-deps-glew/ | grep -oE 'https://.*kivy_deps.glew-0.2.0-cp37-cp37m-win_amd64.whl#'`
${WGET} `${CURL} -s https://pypi.org/simple/kivy-deps-angle/ | grep -oE 'https://.*kivy_deps.angle-0.2.0-cp37-cp37m-win_amd64.whl#'`

# misc linux
${WGET} https://github.com/niess/python-appimage/releases/download/python3.7/python3.7.8-cp37-cp37m-manylinux2014_x86_64.AppImage
${WGET} https://github.com/AppImage/AppImageKit/releases/download/12/appimagetool-x86_64.AppImage
${WGET} --output-document=squashfs4.4.tar.gz https://sourceforge.net/projects/squashfs/files/squashfs/squashfs4.4/squashfs4.4.tar.gz/download

# misc windows
${WGET} https://www.python.org/ftp/python/3.7.8/python-3.7.8-amd64.exe

# misc macos
${WGET} https://github.com/libusb/libusb/releases/download/v1.0.23/libusb-1.0.23.tar.bz2
${WGET} https://homebrew.bintray.com/bottles/wget-1.20.3_2.catalina.bottle.tar.gz
${WGET} https://homebrew.bintray.com/bottles/python-3.7.8.catalina.bottle.tar.gz
${WGET} https://homebrew.bintray.com/bottles/sdl2-2.0.12_1.catalina.bottle.tar.gz
${WGET} https://homebrew.bintray.com/bottles/sdl2_image-2.0.5.catalina.bottle.tar.gz
${WGET} https://homebrew.bintray.com/bottles/sdl2_ttf-2.0.15.catalina.bottle.tar.gz
${WGET} https://homebrew.bintray.com/bottles/sdl2_mixer-2.0.4.catalina.bottle.tar.gz
${WGET} https://homebrew.bintray.com/bottles/libmodplug-0.8.9.0.catalina.bottle.1.tar.gz

# get checksums
sha256sum *
