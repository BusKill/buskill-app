#!/bin/bash
set -x
################################################################################
# File:    mac/buildDmg.sh
# Purpose: Builds a self-contained dmg for a simple Hello World
#          GUI app using kivy. See also:
#
#          * https://kivy.org/doc/stable/installation/installation-osx.html
#          * https://kivy.org/doc/stable/guide/packaging-osx.html
#          * https://blog.fossasia.org/deploying-a-kivy-application-with-pyinstaller-for-mac-osx-to-github/
#
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-06-22
# Updated: 2020-06-22
# Version: 0.1
################################################################################


############
# SETTINGS #
############

PYTHON_PATH='/usr/local/bin/python3'
APP_NAME='helloWorld'

PYTHON_VERSION="`${PYTHON_PATH} --version | cut -d' ' -f2`"
PYTHON_EXEC_VERSION="`echo ${PYTHON_VERSION} | cut -d. -f1-2`"

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

#####################
# PYINSTALLER BUILD #
#####################

mkdir pyinstaller
pushd pyinstaller

${PYTHON_PATH} -m PyInstaller -y --clean --windowed --name ${APP_NAME} \
  --hidden-import 'pkg_resources.py2_warn' \
  --exclude-module _tkinter \
  --exclude-module Tkinter \
  --exclude-module enchant \
  --exclude-module twisted \
  ../src/main.py

pushd dist
hdiutil create ./${APP_NAME}.dmg -srcfolder ${APP_NAME}.app -ov
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
