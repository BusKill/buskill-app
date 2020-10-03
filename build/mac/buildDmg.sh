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
# Updated: 2020-09-17
# Version: 0.4
################################################################################

############
# SETTINGS #
############

PYTHON_PATH="`find /usr/local/Cellar/python@3.7 -type f -name python3.7 | head -n1`"
PIP_PATH="`find /usr/local/Cellar/python@3.7 -type f -name pip3.7 | head -n1`"
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
${PYTHON_PATH} -m pip list
which pip3
pip3 list
ls -lah /usr/local/opt/python/libexec/
ls -lah /usr/local/opt/python/libexec/bin
ls -lah /usr/local/bin | grep -Ei 'pip|python'
find /usr/local/Cellar | grep -i 'bin/pip'
brew list
brew info python
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

VERSION=`git symbolic-ref HEAD | head -n1 | awk -F '/' '{print $NF}'`
if [[ "${VERSION}" = "dev" ]]; then
	VERSION="${SOURCE_DATE_EPOCH}"
fi

DMG_FILENAME="${APP_NAME}-mac-${VERSION}-x86_64.dmg"
APP_DIR_NAME="${APP_NAME}-${VERSION}.app"

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
ls -lah ${cacheDir}

# install os-level depends
brew reinstall build/deps/wget-1.20.3_2.catalina.bottle.tar.gz

brew -v uninstall --ignore-dependencies python
brew -v reinstall build/deps/python-3.7.8.catalina.bottle.tar.gz

brew reinstall build/deps/libmodplug-0.8.9.0.catalina.bottle.1.tar.gz
brew reinstall build/deps/sdl2-2.0.12_1.catalina.bottle.tar.gz
brew reinstall build/deps/sdl2_image-2.0.5.catalina.bottle.tar.gz
brew reinstall build/deps/sdl2_mixer-2.0.4.catalina.bottle.tar.gz
brew reinstall build/deps/sdl2_ttf-2.0.15.catalina.bottle.tar.gz

# check contents of pip binary
cat ${PIP_PATH}

# get python essential dependencies
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/pip-20.1.1-py2.py3-none-any.whl
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/setuptools-49.1.0-py3-none-any.whl
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/wheel-0.34.2-py2.py3-none-any.whl

# install kivy and all other python dependencies with pip
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/Kivy-1.11.1-cp37-cp37m-macosx_10_6_intel.macosx_10_9_intel.macosx_10_9_x86_64.macosx_10_10_intel.macosx_10_10_x86_64.whl
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/libusb1-1.8.tar.gz
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/PyInstaller-3.6.tar.gz

# INSTALL LATEST PIP PACKAGES
# (this can only be done for packages that are cryptographically signed
#  by the developer)

# (temporarily) re-enable internet access
export all_proxy=''

# python-gnupg
#  * https://bitbucket.org/vinay.sajip/python-gnupg/issues/137/pgp-key-accessibility
#  * https://github.com/BusKill/buskill-app/issues/6#issuecomment-682971392
tmpDir="`mktemp -d`" || exit 1
pushd "${tmpDir}"
${PIP_PATH} download python-gnupg
filename="`ls -1 | head -n1`"
signature_url=`curl -s https://pypi.org/simple/python-gnupg/ | grep -oE "https://.*${filename}#" | sed 's/#/.asc/'`
wget "${signature_url}"

mkdir gnupg
chmod 0700 gnupg
popd
gpg --homedir "${tmpDir}/gnupg" --import "build/deps/python-gnupg.asc"
gpgv --homedir "${tmpDir}/gnupg" --keyring "${tmpDir}/gnupg/pubring.kbx" "${tmpDir}/${filename}.asc" "${tmpDir}/${filename}"

# confirm that the signature is valid. `gpgv` would exit 2 if the signature
# isn't in our keyring (so we are effectively pinning it), it exits 1 if there's
# any BAD signatures, and exits 0 "if everything is fine"
if [[ $? -ne 0 ]]; then
	echo "ERROR: Invalid PGP signature!"
	exit 1
fi
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links "file:///${tmpDir}" "${tmpDir}/${filename}"
rm -rf "${tmpDir}"

# re-disable internet access
export all_proxy='http://example.com:9999'

# OTHER NON-PIP DEPENDS

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
 'VERSION': '${VERSION}',
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

cat > ${APP_NAME}.spec <<EOF
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['../src/main.py'],
             pathex=['./'],
             binaries=[],
             datas=[
              ( '../KEYS', '.' ),
              ('../src/images/buskill-icon-150.png', '.')
              ('/usr/local/bin/gpg', '.')
             ],
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
             name='${APP_DIR_NAME}',
             icon='buskill-icon-150.png',
             bundle_identifier=None)
EOF

${PYTHON_PATH} -m PyInstaller -y --clean --windowed "${APP_NAME}.spec"

pushd dist
ls -lah

########################
# ADD ADDITIONAL FILES #
########################

# now let's add some additional files to our release for the user, which will
# be *outside* the AppImage

# docs/
docsDir="${APP_DIR_NAME}/docs"
mkdir -p "${docsDir}"

cp "../../docs/README.md" "${docsDir}/"
cp "../../docs/attribution.rst" "${docsDir}/"
cp "../../LICENSE" "${docsDir}/"
cp "../../CHANGELOG" "${docsDir}/"
cp "../../KEYS" "${docsDir}/"

# change the timestamps of all the files in the appdir for reproducible builds
find ${APP_DIR_NAME} -exec touch -h -d "@${SOURCE_DATE_EPOCH}" {} +

ls -lah "${APP_DIR_NAME}"
ls -lah "${docsDir}"

############
# MAKE DMG #
############

# we make a (7-zip compresssed) dmg image instead of a tarball for MacOS

hdiutil create ./${DMG_FILENAME} -srcfolder ${APP_DIR_NAME} -ov
touch -h -d "@${SOURCE_DATE_EPOCH}" "${DMG_FILENAME}"

popd

#####################
# PREPARE ARTIFACTS #
#####################

# create the dist dir for our result to be uploaded as an artifact
mkdir -p ../dist
cp "dist/${DMG_FILENAME}" ../dist/

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
${PYTHON_PATH} -m pip list
which pip3
pip3 list
ls -lah /usr/local/opt/python/libexec/
ls -lah /usr/local/opt/python/libexec/bin
ls -lah /usr/local/bin | grep -Ei 'pip|python'
find /usr/local/Cellar | grep -i 'bin/pip'
brew list
brew info python
echo $PATH
pwd
ls -lah
ls -lah dist

##################
# CLEANUP & EXIT #
##################

# exit cleanly
exit 0
