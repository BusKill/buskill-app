#!/bin/bash
set -x
################################################################################
# File:    mac/buildDmg.sh
# Purpose: Builds a self-contained dmg for buskill. See also:
#          * https://kivy.org/doc/stable/installation/installation-osx.html
#          * https://kivy.org/doc/stable/guide/packaging-osx.html
#          * https://blog.fossasia.org/deploying-a-kivy-application-with-pyinstaller-for-mac-osx-to-github/
#
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-06-24
# Updated: 2020-07-09
# Version: 0.3
################################################################################

############
# SETTINGS #
############

PYTHON_PATH='/usr/local/bin/python3'
APP_NAME='buskill'

PYTHON_VERSION="`${PYTHON_PATH} --version | cut -d' ' -f2`"
PYTHON_EXEC_VERSION="`echo ${PYTHON_VERSION} | cut -d. -f1-2`"

# make PyInstaller produce reproducible builds. This will only affect the hash
# randomization at build time. When the frozen app built by PyInstaller is
# executed, hash randomization will be enabled (per defaults)
# * https://pyinstaller.readthedocs.io/en/stable/advanced-topics.html#creating-a-reproducible-build
# * https://docs.python.org/3/using/cmdline.html#cmdoption-r
export PYTHONHASHSEED=1

# https://reproducible-builds.org/docs/source-date-epoch/
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)

# prevent brew from accessing the Internet, since it doesn't do cryptographic
# authentication and integrity checks and could be a vector for MITM attacks
# poisoning our builds
export HOMEBREW_NO_AUTO_UPDATE=1
export all_proxy='http://example.com:9999'
export HOMEBREW_CACHE="`pwd`/build/deps/"

########
# INFO #
########

# print some info for debugging failed builds
uname -a
sw_vers
which python2
python2 --version
which python3
python3 --version
${PYTHON_PATH} --version
echo $PATH
pwd
ls -lah
env

#################
# FIX CONSTANTS #
#################

# fill-in some constants if this script is not being run on GitHub
if [ -z ${GITHUB_SHA} ]; then
	GITHUB_SHA=`git show-ref | head -n1 | awk '{print $1}'`
fi

if [ -z ${GITHUB_REF} ]; then
	GITHUB_REF=`git show-ref | head -n1 | awk '{print $2}'`
fi

###################
# INSTALL DEPENDS #
###################

# first update brew
#  * https://blog.fossasia.org/deploying-a-kivy-application-with-pyinstaller-for-mac-osx-to-github/
# strke that. let's *not* pull updates through an insecure pipe
#  * https://github.com/BusKill/buskill-app/issues/2
#brew update

# copy all our brew depends into the brew cache dir
cacheDir=`brew --cache`
cp build/deps/*bottle* ${cacheDir}/

# install os-level depends
brew reinstall --cache build/deps/ build/deps/wget-1.20.3_2.catalina.bottle.tar.gz
brew reinstall --cache build/deps/ build/deps/python-3.7.8.catalina.bottle.tar.gz
brew reinstall --cache build/deps/ build/deps/sdl2-2.0.12_1.catalina.bottle.tar.gz
brew reinstall --cache build/deps/ build/deps/sdl2_image-2.0.5.catalina.bottle.tar.gz
brew reinstall --cache build/deps/ build/deps/sdl2_mixer-2.0.4.catalina.bottle.tar.gz
brew reinstall --cache build/deps/ build/deps/sdl2_ttf-2.0.15.catalina.bottle.tar.gz

# get python essential dependencies
${PYTHON_PATH} -m pip install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/pip-20.1.1-py2.py3-none-any.whl
${PYTHON_PATH} -m pip install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/setuptools-49.1.0-py3-none-any.whl
${PYTHON_PATH} -m pip install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/wheel-0.34.2-py2.py3-none-any.whl

# install kivy and all other python dependencies with pip
${PYTHON_PATH} -m pip install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/Kivy-1.11.1-cp37-cp37m-macosx_10_6_intel.macosx_10_9_intel.macosx_10_9_x86_64.macosx_10_10_intel.macosx_10_10_x86_64.whl
${PYTHON_PATH} -m pip install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/libusb1-1.8.tar.gz
${PYTHON_PATH} -m pip install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/PyInstaller-3.6.tar.gz

# libusb depend for MacOS, from:
# * https://libusb.info/
# * https://github.com/libusb/libusb/releases/download/v1.0.23/libusb-1.0.23.tar.bz2
cp build/deps/libusb-1.0.23.tar.bz2 /tmp/
pushd /tmp
tar -xjvf libusb-1.0.23.tar.bz2
pushd libusb-1.0.23
./configure
make
popd
popd
find /tmp | grep -i dylib
cp /tmp/libusb-1.0.23/libusb/.libs/libusb-1.0.dylib src/

# output information about this build so the code can use it later in logs
cat > src/buskill_version.py <<EOF
BUSKILL_VERSION = {
 'GITHUB_REF': '${GITHUB_REF}',
 'GITHUB_SHA': '${GITHUB_SHA}',
 'SOURCE_DATE_EPOCH': '${SOURCE_DATE_EPOCH}',
}
EOF

#####################
# PYINSTALLER BUILD #
#####################

mkdir pyinstaller
pushd pyinstaller

cat >> ${APP_NAME}.spec <<EOF
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['../src/main.py'],
             pathex=['./'],
             binaries=[],
             datas=[],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['_tkinter', 'Tkinter', 'enchant', 'twisted'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='${APP_NAME}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe, Tree('../src/'),
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='${APP_NAME}')
app = BUNDLE(coll,
             name='${APP_NAME}.app',
             icon=None,
             bundle_identifier=None)
EOF

${PYTHON_PATH} -m PyInstaller -y --clean --windowed "${APP_NAME}.spec"

pushd dist

# change the timestamps of all the files in the appdir or reproducable builds
find ${APP_NAME}.app -exec touch -h -d "@${SOURCE_DATE_EPOCH}" {} +

hdiutil create ./${APP_NAME}.dmg -srcfolder ${APP_NAME}.app -ov
touch -h -d "@${SOURCE_DATE_EPOCH}" "${APP_NAME}.dmg"

popd

#####################
# PREPARE ARTIFACTS #
#####################

# create the dist dir for our result to be uploaded as an artifact
mkdir -p ../dist
cp "dist/${APP_NAME}.dmg" ../dist/

#######################
# OUTPUT VERSION INFO #
#######################

uname -a
sw_vers
which python2
python2 --version
which python3
python3 --version
${PYTHON_PATH} --version
echo $PATH
pwd
ls -lah
ls -lah dist

##################
# CLEANUP & EXIT #
##################

# exit cleanly
exit 0
