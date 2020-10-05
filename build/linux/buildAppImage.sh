#!/bin/bash
set -x
################################################################################
# File:    linux/buildAppImage.sh
# Purpose: Builds a self-contained AppImage executable for a simple Hello World
#          GUI app using kivy. See also:
#
#          * https://kivy.org/doc/stable/installation/installation-linux.html
#          * https://kivy.org/doc/stable/guide/basic.html
#          * https://github.com/AppImage/AppImageKit/wiki/Bundling-Python-apps
#
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-05-30
# Updated: 2020-10-03
# Version: 1.0
################################################################################

################################################################################
#                                  SETTINGS                                    #
################################################################################

APP_NAME='buskill' 
# prevent apt from asking for things we can't respond to
export DEBIAN_FRONTEND=noninteractive

SUDO='/usr/bin/sudo'
PYTHON='/tmp/kivy_appdir/AppRun'

# this is the command we use to run commands as the _apt user so they have
# internet (only use this for apps that are trustworthy. eg: not pip)
SU='/bin/su _apt -s /bin/bash'

# check to see if we're inside a docker container or not
# https://stackoverflow.com/a/51688023/1174102
INODE_NUM=`ls -ali / | sed '2!d' |awk {'print $1'}`
if [ $INODE_NUM -gt 3 ]; then
	# a high inode means we're in docker, and in docker we don't use sudo
	echo "INFO: Detected execution inside docker container"
	SUDO=''
fi

################################################################################
#                                  FUNCTIONS                                   #
################################################################################

print_debugging_info () {
	date
	uname -a
	cat /etc/issue
	which gpg
	gpg --version
	which gpg2
	gpg2 --version
	sha256sum /usr/bin/gpg
	which python
	python --version
	python -m pip list
	ls -lah /tmp/kivy_appdir/opt/python*/bin/python*
	ls -lah "/tmp/kivy_appdir/opt/python3.7/lib/python3.7/site-packages/"
	/tmp/kivy_appdir/opt/python*/bin/python* --version
	/tmp/kivy_appdir/opt/python*/bin/python* -m pip list
	dpkg --list --no-pager || dpkg --list # fucking Ubuntu
	whoami
	env
}

################################################################################
#                                 MAIN BODY                                    #
################################################################################

#################
# SANITY CHECKS #
#################

# this script isn't robust enough
if [ ! -e "`pwd`/build/linux/buildAppImage.sh" ]; then
	echo "ERROR: This script should only be executed from the root of the github dir."
	exit 1
fi
	
###############
# OUTPUT INFO #
###############

# output info to debug issues with this build
print_debugging_info

###################
# INSTALL DEPENDS #
###################

${SUDO} rm -rf /var/lib/apt/lists/*
${SUDO} apt-get clean
${SUDO} apt-get update -o Acquire::CompressionTypes::Order::=gz || exit 1
#${SUDO} apt-get update || exit 1
${SUDO} apt-get -y install iptables git python3-pip python3-setuptools python3-virtualenv rsync curl wget gnupg

#################
# FIX CONSTANTS #
#################

# https://reproducible-builds.org/docs/source-date-epoch/
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)

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

ARCHIVE_DIR="buskill-lin-${VERSION}-x86_64"

##################
# SETUP IPTABLES #
##################

# We setup iptables so that only the apt user (and therefore the apt command)
# can access the internet. We don't want insecure tools like `pip` to download
# unsafe code from the internet.

${SUDO} iptables-save > /tmp/iptables-save.`date "+%Y%m%d_%H%M%S"`
${SUDO} iptables -A INPUT -i lo -j ACCEPT
${SUDO} iptables -A INPUT -s 127.0.0.1/32 -j DROP
${SUDO} iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
${SUDO} iptables -A INPUT -j DROP
${SUDO} iptables -A OUTPUT -s 127.0.0.1/32 -d 127.0.0.1/32 -j ACCEPT
${SUDO} iptables -A OUTPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
${SUDO} iptables -A OUTPUT -m owner --uid-owner 100 -j ACCEPT # apt uid = 100

# TODO: simplify these tests
${SUDO} iptables -A OUTPUT -m owner --uid-owner provisioner -j ACCEPT
${SUDO} iptables -A OUTPUT -m owner --uid-owner runneradmin -j ACCEPT
${SUDO} iptables -A OUTPUT -m owner --uid-owner runner -j ACCEPT
${SUDO} iptables -A OUTPUT -d 10.1.0.0/16 -j ACCEPT

${SUDO} iptables -A OUTPUT -j DROP

${SUDO} ip6tables-save > /tmp/ip6tables-save.`date "+%Y%m%d_%H%M%S"`
${SUDO} ip6tables -A INPUT -i lo -j ACCEPT
${SUDO} ip6tables -A INPUT -s ::1/128 -j DROP
${SUDO} ip6tables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
${SUDO} ip6tables -A INPUT -j DROP
${SUDO} ip6tables -A OUTPUT -s ::1/128 -d ::1/128 -j ACCEPT
${SUDO} ip6tables -A OUTPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
${SUDO} ip6tables -A OUTPUT -m owner --uid-owner 100 -j ACCEPT
${SUDO} ip6tables -A OUTPUT -j DROP

# attempt to access the internet as root. If it works, exit 1
curl 1.1.1.1
if [ $? -eq 0 ]; then
	echo "ERROR: iptables isn't blocking internet access to unsafe tools. You may need to run this as root (and you should do it inside a VM)"
	exit 1
fi

##################
# PREPARE APPDIR #
##################

# first cleanup old tmp files/dirs, if needed
rm -f /tmp/pyhon.AppImage
rm -f /tmp/appimagetool.AppImage
rm -f /tmp/squashfs4.4.tar.gz
rm -rf /tmp/kivy_appdir
rm -rf /tmp/appimagetool_appdir
rm -rf /tmp/squashfs4.4

# We use this python-appimage release as a base for building our own python
# AppImage. We only have to add our code and depends to it.
cp build/deps/python3.7.8-cp37-cp37m-manylinux2014_x86_64.AppImage /tmp/python.AppImage
chmod +x /tmp/python.AppImage
pushd /tmp
/tmp/python.AppImage --appimage-extract
popd
rm -rf /tmp/kivy_appdir
mv /tmp/squashfs-root/* /tmp/kivy_appdir
mv /tmp/squashfs-root/.* /tmp/kivy_appdir

# for debugging reproducible builds
sha256sum /tmp/python.AppImage
ls -lah /tmp/kivy_appdir
ls -lah /tmp/kivy_appdir/usr/bin/

# INSTALL LOCAL PIP PACKAGES

# install our pip depends from the files in the repo since pip doesn't provide
# decent authentication and integrity checks on what it downloads from PyPI
#  * https://security.stackexchange.com/a/234098/213165
${PYTHON} -m pip install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file:///`pwd`/build/deps/ build/deps/pip-20.1.1-py2.py3-none-any.whl
${PYTHON} -m pip install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file:///`pwd`/build/deps/ build/deps/Kivy-1.11.1-cp37-cp37m-manylinux2010_x86_64.whl
${PYTHON} -m pip install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file:///`pwd`/build/deps/ build/deps/libusb1-1.8.tar.gz

# INSTALL LATEST PIP PACKAGES
# (this can only be done for packages that are cryptographically signed
#  by the developer)

# python-gnupg
#  * https://bitbucket.org/vinay.sajip/python-gnupg/issues/137/pgp-key-accessibility
#  * https://github.com/BusKill/buskill-app/issues/6#issuecomment-682971392
tmpDir="`mktemp -d`" || exit 1
chown _apt:root "${tmpDir}"
pushd "${tmpDir}"
${SU} -c "${PYTHON} -m pip download python-gnupg"
filename="`ls -1 | head -n1`"
signature_url=`${SU} -c "curl -s https://pypi.org/simple/python-gnupg/" | grep -oE "https://.*${filename}#" | sed 's/#/.asc/'`
${SU} -c "wget \"${signature_url}\""

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
${PYTHON} -m pip install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links "file:///${tmpDir}" "${tmpDir}/${filename}"
rm -rf "${tmpDir}"

# add our code to the AppDir
rsync -a src /tmp/kivy_appdir/opt/

# also add our KEYS file
cp KEYS /tmp/kivy_appdir/opt/src/

# and our gpg binary
cp /usr/bin/gpg /tmp/kivy_appdir/opt/src/

# replace kivy icons with our icons since kivy has a bug with icons in linux
#  * https://github.com/kivy/kivy/issues/2202
cp src/images/buskill-icon-128.png /tmp/kivy_appdir/opt/python3.7/lib/python3.7/site-packages/kivy/data/logo/kivy-icon-128.png
cp src/images/buskill-icon-64.png /tmp/kivy_appdir/opt/python3.7/lib/python3.7/site-packages/kivy/data/logo/kivy-icon-64.png
cp src/images/buskill-icon-48.png /tmp/kivy_appdir/opt/python3.7/lib/python3.7/site-packages/kivy/data/logo/kivy-icon-48.png
cp src/images/buskill-icon-32.png /tmp/kivy_appdir/opt/python3.7/lib/python3.7/site-packages/kivy/data/logo/kivy-icon-32.png
cp src/images/buskill-icon-24.png /tmp/kivy_appdir/opt/python3.7/lib/python3.7/site-packages/kivy/data/logo/kivy-icon-25.png
cp src/images/buskill-icon-16.png /tmp/kivy_appdir/opt/python3.7/lib/python3.7/site-packages/kivy/data/logo/kivy-icon-16.png

# output information about this build so the code can use it later in logs
cat > /tmp/kivy_appdir/opt/src/buskill_version.py <<EOF
BUSKILL_VERSION = {
 'VERSION': '${VERSION}',
 'GITHUB_REF': '${GITHUB_REF}',
 'GITHUB_SHA': '${GITHUB_SHA}',
 'SOURCE_DATE_EPOCH': '${SOURCE_DATE_EPOCH}',
}
EOF
cat /tmp/kivy_appdir/opt/src/buskill_version.py

# change AppRun so it executes our app
rm /tmp/kivy_appdir/AppRun
cat > /tmp/kivy_appdir/AppRun <<'EOF'
#! /bin/bash

# Export APPRUN if running from an extracted image
self="$(readlink -f -- $0)"
here="${self%/*}"
APPDIR="${APPDIR:-${here}}"

# Export TCl/Tk
export TCL_LIBRARY="${APPDIR}/usr/share/tcltk/tcl8.5"
export TK_LIBRARY="${APPDIR}/usr/share/tcltk/tk8.5"
export TKPATH="${TK_LIBRARY}"

# Call the entry point
for opt in "$@"
do
    [ "${opt:0:1}" != "-" ] && break
    if [[ "${opt}" =~ "I" ]] || [[ "${opt}" =~ "E" ]]; then
        # Environment variables are disabled ($PYTHONHOME). Let's run in a safe
        # mode from the raw Python binary inside the AppImage
        "$APPDIR/opt/python3.7/bin/python3.7 $APPDIR/opt/src/main.py" "$@"
        exit "$?"
    fi
done

# Get the executable name, i.e. the AppImage or the python binary if running from an
# extracted image
executable="${APPDIR}/opt/python3.7/bin/python3.7 ${APPDIR}/opt/src/main.py"
if [[ "${ARGV0}" =~ "/" ]]; then
    executable="$(cd $(dirname ${ARGV0}) && pwd)/$(basename ${ARGV0})"
elif [[ "${ARGV0}" != "" ]]; then
    executable=$(which "${ARGV0}")
fi

# Wrap the call to Python in order to mimic a call from the source
# executable ($ARGV0), but potentially located outside of the Python
# install ($PYTHONHOME)
(PYTHONHOME="${APPDIR}/opt/python3.7" exec -a "${executable}" "$APPDIR/opt/python3.7/bin/python3.7" "$APPDIR/opt/src/main.py" "$@")
exit "$?"
EOF

# make it executable
chmod +x /tmp/kivy_appdir/AppRun

# change the timestamps of all the files in the appdir or reproducible builds
find /tmp/kivy_appdir -exec touch -h -d "@${SOURCE_DATE_EPOCH}" {} +

############
# THINNING #
############

# first print the pip packags installed before the thinning deletes pip
/tmp/kivy_appdir/opt/python*/bin/python* -m pip list

echo "INFO: Beginning AppDir thinning"

# remove some unnecessary items from the AppDir to reduce the AppImage size
# and make the AppImage reproducible

unnecessary="__pycache__ pip pygments docutils setuptools chardet urllib3 elftools pkg_resources kivy-examples requests direct_url.json RECORD"
for item in $(echo "${unnecessary}"); do

	paths=`find /tmp/kivy_appdir -iname "*${item}*"`

	for path in $(echo "${paths}"); do
		if [ -e ]; then
			echo "INFO: deleting $path "
			rm -rf "${path}"
		fi
	done

done

########################
# PREPARE APPIMAGETOOL #
########################

cp build/deps/appimagetool-x86_64.AppImage /tmp/appimagetool.AppImage
chmod +x /tmp/appimagetool.AppImage

cp build/deps/squashfs4.4.tar.gz /tmp/

pushd /tmp

# The latest stable appimagetool uses an old version of mksquashfs (v4.3),
# which does not support reproducible builds. Here we build the latest
# squashfs-tools (v4.4) and hack appimagetools to use it. For more info, see:
#  * https://github.com/BusKill/buskill-app/issues/3
tar -xzvf squashfs4.4.tar.gz
pushd squashfs4.4/squashfs-tools
${SUDO} apt-get -y install zlib1g-dev make
make
popd

/tmp/appimagetool.AppImage --appimage-extract
mv /tmp/squashfs-root /tmp/appimagetool_appdir
mv /tmp/appimagetool_appdir/usr/lib/appimagekit/mksquashfs /tmp/appimagetool_appdir/usr/lib/appimagekit/mksquashfs.orig

cat > /tmp/appimagetool_appdir/usr/lib/appimagekit/mksquashfs <<EOF
#!/bin/sh

export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH}"

# the new version of mksquashfs no longer supports the '-mkfs-fixed-time'
# argument, so we remove it
args=\$(echo "\$@" | sed -e 's/-mkfs-fixed-time 0//')
/tmp/squashfs4.4/squashfs-tools/mksquashfs \$args
EOF

chmod +x /tmp/appimagetool_appdir/usr/lib/appimagekit/mksquashfs

popd # leave /tmp

##################
# BUILD APPIMAGE #
##################

# attempting to fix permission mixmatch for reproducible builds
${SUDO} chmod -R 0644 /tmp/kivy_appdir
${SUDO} find /tmp/kivy_appdir -type d -exec chmod 0755 '{}' \;
${SUDO} chmod 0755 /tmp/kivy_appdir/AppRun
${SUDO} chmod 0755 /tmp/kivy_appdir/opt/python*/bin/python*

# create the dist dir for our result to be uploaded as an artifact
# note tha gitlab will only accept artifacts that are in the build dir (cwd)
mkdir -p "dist/${ARCHIVE_DIR}"

# create the AppImage from kivy AppDir
/tmp/appimagetool_appdir/AppRun --no-appstream "/tmp/kivy_appdir" "dist/${ARCHIVE_DIR}/${APP_NAME}-${VERSION}.AppImage"
sha256sum "dist/${ARCHIVE_DIR}/${APP_NAME}-${VERSION}.AppImage"

########################
# ADD ADDITIONAL FILES #
########################

# now let's add some additional files to our release for the user, which will
# be *outside* the AppImage

# docs/
docsDir="dist/${ARCHIVE_DIR}/docs"
mkdir -p "${docsDir}"

cp "docs/README.md" "${docsDir}/"
cp "docs/attribution.rst" "${docsDir}/"
cp "LICENSE" "${docsDir}/"
cp "CHANGELOG" "${docsDir}/"
cp "KEYS" "${docsDir}/"

###############
# OUTPUT INFO #
###############

# output info to debug issues with this build
print_debugging_info

##################
# CLEANUP & EXIT #
##################

# exit cleanly
exit 0
