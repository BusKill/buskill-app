#!/bin/bash
set -x
################################################################################
# File:    mac/buildDmg.sh
# Purpose: Builds a self-contained dmg for a simple Hello World
#          GUI app using kivy. See also:
#
#          * https://kivy.org/doc/stable/installation/installation-osx.html
#          * https://kivy.org/doc/stable/guide/packaging-osx.html
#          * https://github.com/kivy/buildozer/issues/494#issuecomment-390262889
#
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-06-22
# Updated: 2020-06-22
# Version: 0.1
################################################################################


############
# SETTINGS #
############

PYTHON_PATH='/usr/bin/python3'
APP_NAME='helloWorld'

PYTHON_VERSION="`${PYTHON_PATH} --version | cut -d' ' -f2`"
PYTHON_EXEC_VERSION="`echo ${PYTHON_VERSION} | cut -d. -f1-2`"

# attempt to overwrite brew's /usr/local/bin/python3 with /usr/bin/python3
#alias python3='${PYTHON_PATH}'

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

echo "INFO: list of python* in /usr/bin/"
ls -lah /usr/bin/python*
find /usr/bin -type f -name python | xargs --version
find /usr/bin -type f -name python3 | xargs --version
md5 /usr/bin/python*

echo "INFO: list of python* in /usr/local/bin/"
ls -lah /usr/local/bin/python*
find /usr/local/bin -type f -name python | xargs --version
find /usr/local/bin -type f -name python3 | xargs --version
md5 /usr/local/bin/python*

###################
# INSTALL DEPENDS #
###################

# install os-level depends
brew install wget
brew reinstall --build-bottle sdl2 sdl2_image sdl2_ttf sdl2_mixer

# setup a virtualenv to isolate our app's python depends
sudo ${PYTHON_PATH} -m ensurepip
${PYTHON_PATH} -m pip install --upgrade --user pip setuptools
#${PYTHON_PATH} -m pip install --upgrade --user virtualenv
#${PYTHON_PATH} -m virtualenv /tmp/kivy_venv

# install kivy and all other python dependencies with pip into our virtual env
#source /tmp/kivy_venv/bin/activate
${PYTHON_PATH} -m pip install Cython==0.29.10
${PYTHON_PATH} -m pip install -r requirements.txt

#######################
# PREPARE PYINSTALLER #
#######################

mkdir pyinstaller
pushd pyinstaller

# TODO: change this to cat
pyinstaller -y --clean --windowed --name ${APP_NAME} \
  --exclude-module _tkinter \
  --exclude-module Tkinter \
  --exclude-module enchant \
  --exclude-module twisted \
  ../src/main.py

#########
# BUILD #
#########

pyinstaller -y --clean --windowed ${APP_NAME}.spec

pushd dist
hdiutil create ./${APP_NAME}.dmg -srcfolder ${APP_NAME}.app -ov
popd

#####################
# PREPARE ARTIFACTS #
#####################

# TODO: remove this after fixing .dmg generation
# the dmg generation below fails on headless builds because you have to click
# a button in a dialog granting finder some permissions from the apple script.
# for now we include the .app
mkdir -p ../dist
cp -r "${APP_NAME}.app" ../dist/

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
pwd
echo $PATH
ls -lah /Users/runner/Library/Python/3.7/bin
ls -lah
ls -lah dist

##################
# CLEANUP & EXIT #
##################

# exit cleanly
exit 0
