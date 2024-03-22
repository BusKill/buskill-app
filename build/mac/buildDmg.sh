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
# Updated: 2024-03-22
# Version: 1.0
################################################################################

################################################################################
#                                  SETTINGS                                    #
################################################################################

PYTHON_PATH="`find /usr/local/Cellar/python* -type f -wholename *bin/python3* | sort -n | uniq | head -n1`"
PIP_PATH="`find /usr/local/Cellar/python* -type f -wholename *bin/pip3* | sort -n | uniq | head -n1`"
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

################################################################################
#                                  FUNCTIONS                                   #
################################################################################

# print some info for debugging failed builds
print_debugging_info () {
	date
	uname -a
	sw_vers
	find /usr/local/Cellar -maxdepth 1
	which python2
	python2 --version
	which python3
	python3 --version
	${PYTHON_PATH} --version
	${PIP_PATH} --version
	${PYTHON_PATH} -m pip list
	which pip3
	pip3 list
	#ls -lah /usr/local/opt/python/libexec/
	#ls -lah /usr/local/opt/python/libexec/bin
	#ls -lah /usr/local/bin | grep -Ei 'pip|python'
	#find /usr/local/Cellar | grep -i 'bin/pip'
	#find /usr/local/Cellar/python -type f
	#find /usr/local/Cellar/python -type f | grep -i 'bin/python3'
	#find /usr/local/Cellar/python -type f | grep -i 'bin/pip3'
	#find /usr/local/Cellar/python -type f -ipath *bin/python3*
	#find /usr/local/Cellar/python -type f -ipath *bin/pip3*
	find /usr/local/Cellar/python* -type f -wholename *bin/python3*
	find /usr/local/Cellar/python* -type f -wholename *bin/pip3*
	brew list
	brew info python
	echo $PATH
	pwd
	ls -lah
	env
}

################################################################################
#                                 MAIN BODY                                    #
################################################################################

# info for debugging failed builds
print_debugging_info

#################
# FIX CONSTANTS #
#################

# don't let "dubious ownership" limit us from continuing
# * https://github.com/BusKill/buskill-app/issues/73#issuecomment-1595819955
git config --global --add safe.directory /root/buskill-app

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

#################
# SANITY CHECKS #
#################

# this script isn't robust enough
if [ ! -e "`pwd`/build/mac/buildDmg.sh" ]; then
	echo "ERROR: This script should only be executed from the root of the github dir."
	exit 1
fi

###################
# INSTALL DEPENDS #
###################

# first update brew
#  * https://blog.fossasia.org/deploying-a-kivy-application-with-pyinstaller-for-mac-osx-to-github/
# strke that. let's *not* pull updates through an insecure pipe
#  * https://github.com/BusKill/buskill-app/issues/2
#brew update

tmpDir="`mktemp -d`" || exit 1
pushd "${tmpDir}"
git clone https://github.com/BusKill/buskill-app-deps.git

mkdir gnupg
chmod 0700 gnupg
popd
gpg --homedir "${tmpDir}/gnupg" --import "build/deps/buskill.asc"
gpgv --homedir "${tmpDir}/gnupg" --keyring "${tmpDir}/gnupg/pubring.kbx" "${tmpDir}/buskill-app-deps/build/deps/SHA256SUMS.asc" "${tmpDir}/buskill-app-deps/build/deps/SHA256SUMS"

# confirm that the signature is valid. `gpgv` would exit 2 if the signature
# isn't in our keyring (so we are effectively pinning it), it exits 1 if there's
# any BAD signatures, and exits 0 "if everything is fine"
if [[ $? -ne 0 ]]; then
	echo "ERROR: Invalid PGP signature!"
	exit 1
fi

pushd "${tmpDir}/buskill-app-deps/build/deps"
sha256sum --strict --check SHA256SUMS

# confirm that the checksums of all the files match what's expected in the
# the signed SHA256SUSM file.
if [[ $? -ne 0 ]]; then
	echo "ERROR: Invalid checksums!"
	exit 1
fi

# copy all the now-verified files to our actual repo
popd
cat "${tmpDir}/buskill-app-deps/build/deps/SHA256SUMS" | while read line; do
	file_path="${tmpDir}/buskill-app-deps/build/deps/$(echo $line | cut -d' ' -f2)"
	cp ${file_path} build/deps/
done

# copy all our brew depends into the brew cache dir
cacheDir=`brew --cache`
ls -lah ${cacheDir}

# install os-level depends
brew reinstall build/deps/wget-1.20.3_2.catalina.bottle.tar.gz

brew -v uninstall --ignore-dependencies python
brew -v reinstall build/deps/python-3.7.8.catalina.bottle.tar.gz
PYTHON_PATH="`find /usr/local/Cellar/python* -type f -wholename *bin/python3* | sort -n | uniq | head -n1`"

# get more info immediately post-python install
#ls -lah /usr/local/Cellar/python/
#find /usr/local/Cellar/python/ -type f -wholename *bin/python3*

brew reinstall build/deps/libmodplug-0.8.9.0.catalina.bottle.1.tar.gz
brew reinstall build/deps/sdl2-2.0.12_1.catalina.bottle.tar.gz
brew reinstall build/deps/sdl2_image-2.0.5.catalina.bottle.tar.gz
brew reinstall build/deps/sdl2_mixer-2.0.4.catalina.bottle.tar.gz
brew reinstall build/deps/sdl2_ttf-2.0.15.catalina.bottle.tar.gz

# check contents of pip binary
cat ${PIP_PATH}

# get python essential dependencies
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/pip-24.0-py3-none-any.whl
PIP_PATH="`find /usr/local/Cellar/python* -type f -wholename *bin/pip3* | sort -n | uniq | head -n1`"

# get more info post-pip install
#ls -lah /usr/local/Cellar/python/
#find /usr/local/Cellar/python/ -type f -wholename *bin/python3*
#find /usr/local/Cellar/python/ -type f -wholename *bin/pip3*

${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/setuptools-49.1.0-py3-none-any.whl
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/wheel-0.34.2-py2.py3-none-any.whl

# get more info post-python install
#ls -lah /usr/local/Cellar/python/
#find /usr/local/Cellar/python/ -type f -wholename *bin/python3*
#find /usr/local/Cellar/python/ -type f -wholename *bin/pip3*

# install kivy and all other python dependencies with pip
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/Kivy-1.11.1-cp37-cp37m-macosx_10_6_intel.macosx_10_9_intel.macosx_10_9_x86_64.macosx_10_10_intel.macosx_10_10_x86_64.whl
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/pyinstaller-4.7.tar.gz

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

# changing to use the files on GitHub, since the sigs are no longer available
# from PyPI
# * https://github.com/BusKill/buskill-app/issues/78
# TODO: update this to query the GitHub API and grab the latest release
#${PIP_PATH} download python-gnupg
#signature_url=`curl -s https://pypi.org/simple/python-gnupg/ | grep -oE "https://.*${filename}#" | sed 's/#/.asc/'`
file_url='https://github.com/vsajip/python-gnupg/releases/download/0.5.2/python_gnupg-0.5.2-py2.py3-none-any.whl'
signature_url='https://github.com/vsajip/python-gnupg/releases/download/0.5.2/python_gnupg-0.5.2-py2.py3-none-any.whl.asc'

#wget "${signature_url}"
# switching from wget to curl to avoid "dyld Library not loaded" brew issues
#  * https://github.com/BusKill/buskill-app/issues/70
curl --location --remote-name "${file_url}"
filename="`ls -1 | head -n1`"
curl --location --remote-name "${signature_url}"

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

# libusb1
#  * https://github.com/vpelletier/python-libusb1/issues/54
#  * https://github.com/BusKill/buskill-app/issues/17
tmpDir="`mktemp -d`" || exit 1
pushd "${tmpDir}"

# changing to use the files on GitHub, since the sigs are no longer available
# from PyPI
# * https://github.com/BusKill/buskill-app/issues/78
# TODO: update this to query the GitHub API and grab the latest release
#${PIP_PATH} download libusb1
file_url='https://github.com/vpelletier/python-libusb1/releases/download/3.1.0/libusb1-3.1.0-py3-none-any.whl'
signature_url='https://github.com/vpelletier/python-libusb1/releases/download/3.1.0/libusb1-3.1.0-py3-none-any.whl.asc'

#wget "${signature_url}"
# switching from wget to curl to avoid "dyld Library not loaded" brew issues
#  * https://github.com/BusKill/buskill-app/issues/70
curl --location --remote-name "${file_url}"
filename="`ls -1 | head -n1`"
curl --location --remote-name "${signature_url}"

mkdir gnupg
chmod 0700 gnupg
popd
gpg --homedir "${tmpDir}/gnupg" --import "build/deps/libusb1.asc"
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

# gpg depends for MacOS, from:
# * https://github.com/BusKill/buskill-app/issues/36
cp -R /usr/local/opt/gettext/lib/libintl* src/

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

# ICONS
cp ../src/images/buskill-icon-150.png buskill-icon-150.png
sips -i buskill-icon-150.png
DeRez -only icns buskill-icon-150.png > icns.rsrc

# icon set https://stackoverflow.com/a/20703594
mkdir buskill-icon.iconset
sips -z 16 16     buskill-icon-150.png --out buskill-icon.iconset/icon_16x16.png
sips -z 32 32     buskill-icon-150.png --out buskill-icon.iconset/icon_16x16@2x.png
sips -z 32 32     buskill-icon-150.png --out buskill-icon.iconset/icon_32x32.png
sips -z 64 64     buskill-icon-150.png --out buskill-icon.iconset/icon_32x32@2x.png
sips -z 128 128   buskill-icon-150.png --out buskill-icon.iconset/icon_128x128.png
#sips -z 256 256   buskill-icon-150.png --out buskill-icon.iconset/icon_128x128@2x.png
#sips -z 256 256   buskill-icon-150.png --out buskill-icon.iconset/icon_256x256.png
#sips -z 512 512   buskill-icon-150.png --out buskill-icon.iconset/icon_256x256@2x.png
#sips -z 512 512   buskill-icon-150.png --out buskill-icon.iconset/icon_512x512.png
#cp buskill-icon-150.png buskill-icon.iconset/icon_512x512@2x.png
iconutil -c icns buskill-icon.iconset
rm -R buskill-icon.iconset

cat > ${APP_NAME}.spec <<EOF
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['../src/main.py'],
             pathex=['./'],
             binaries=[],
             datas=[
              ( '../KEYS', '.' ),

              # needed for the taskbar icon when the app is running (kivy)
              ('../src/images/buskill-icon-150.png', '.'),

              # needed for the icon of the .app when viewed in Finder
              ('buskill-icon.icns', '.'),

              # needed for gpg https://github.com/BusKill/buskill-app/issues/71
              ('/usr/local/bin/gpg', '.'),
              ('/usr/local/lib/libgcrypt.20.dylib', '.'),
              ('/usr/local/lib/libassuan.0.dylib', '.'),
              ('/usr/local/lib/libnpth.0.dylib', '.'),
              ('/usr/local/lib/libgpg-error.0.dylib', '.')
             ],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['_tkinter', 'Tkinter', 'enchant', 'twisted'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

root_child_mac = Analysis(['../src/packages/buskill/root_child_mac.py'],
             pathex=['./'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['pydoc'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

MERGE( (a, 'a', 'a'), (root_child_mac, 'root_child_mac', 'root_child_mac') )

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

root_child_mac_pyz = PYZ( root_child_mac.pure, root_child_mac.zipped_data,
             cipher=block_cipher)
root_child_mac_exe = EXE(root_child_mac_pyz,
          root_child_mac.scripts,
          [],
          exclude_binaries=True,
          name='root_child_mac',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )

coll = COLLECT(exe, Tree('../src/'),
               a.binaries,
               a.zipfiles,
               a.datas,
               root_child_mac_exe,
               root_child_mac.binaries,
               root_child_mac.zipfiles,
               root_child_mac.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='${APP_NAME}')
app = BUNDLE(coll,
             name='${APP_DIR_NAME}',
             icon='buskill-icon.icns',
             bundle_identifier=None)
EOF
cat ${APP_NAME}.spec

${PYTHON_PATH} -m PyInstaller -y --clean --windowed "${APP_NAME}.spec"

pushd dist
ls -lah

######################
# HARDEN PERMISSIONS #
######################

# the root child scripts must be owned by root:root and 0500 for security reasons
# * https://github.com/BusKill/buskill-app/issues/14#issuecomment-1272449172

root_child_path="${APP_DIR_NAME}/Contents/MacOS/root_child_mac"
chmod 0500 "${root_child_path}"

# unfortunaetly we can't package a .dmg with a file owned by root, and it doesn't
# make sense to do so, anyway
#  * https://github.com/BusKill/buskill-app/issues/14#issuecomment-1279975783
#sudo chown 0:0 "${root_child_path}"

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

# icon
cp "buskill-icon.icns" "${APP_DIR_NAME}/.VolumeIcon.icns"

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

# TODO: fix this so the dmg itself has the buskill icon
# add the dmg icon
Rez -append ../icns.rsrc -o ./${DMG_FILENAME}
SetFile -c icnC "${DMG_FILENAME}/.VolumeIcon.icns"
SetFile -a C ./${DMG_FILENAME}

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

print_debugging_info

##################
# CLEANUP & EXIT #
##################

# exit cleanly
exit 0
