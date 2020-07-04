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
# Updated: 2020-06-24
# Version: 0.2
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
brew update

# install os-level depends
brew install wget python3
brew reinstall sdl2 sdl2_image sdl2_ttf sdl2_mixer

# setup a virtualenv to isolate our app's python depends
sudo ${PYTHON_PATH} -m ensurepip
${PYTHON_PATH} -m pip install --upgrade --user pip setuptools
#${PYTHON_PATH} -m pip install --upgrade --user virtualenv
#${PYTHON_PATH} -m virtualenv /tmp/kivy_venv

# install kivy and all other python dependencies with pip into our virtual env
#source /tmp/kivy_venv/bin/activate
${PYTHON_PATH} -m pip install --upgrade --user Cython==0.29.10
${PYTHON_PATH} -m pip install --upgrade --user -r requirements.txt
${PYTHON_PATH} -m pip install --upgrade --user PyInstaller

# libusb depend for MacOS, extracted from:
# * libusb-1.0.23.tar.bz:libusb/.libs/libusb-1.0.dylib
# * https://libusb.info/
# * https://github.com/libusb/libusb/releases/download/v1.0.23/libusb-1.0.23.tar.bz2
cp build/mac/libusb-1.0.dylib src/

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
