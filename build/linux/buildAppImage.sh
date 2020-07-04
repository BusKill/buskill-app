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
# Updated: 2020-06-25
# Version: 0.3
################################################################################

################################################################################
#                                  SETTINGS                                    #
################################################################################

APP_NAME='buskill'

PYTHON_APPIMAGE_URL='https://github.com/niess/python-appimage/releases/download/python3.7/python3.7.7-cp37-cp37m-manylinux2014_x86_64.AppImage'

# https://reproducible-builds.org/docs/source-date-epoch/
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)

################################################################################
#                                  FUNCTIONS                                   #
################################################################################

print_debugging_info () {
	date
	uname -a
	cat /etc/issue
	which python
	python --version
	python -m pip list
	ls -lah /tmp/kivy_appdir/opt/python*/bin/python*
	/tmp/kivy_appdir/opt/python*/bin/python* --version
	/tmp/kivy_appdir/opt/python*/bin/python* -m pip list
	env
}

################################################################################
#                                 MAIN BODY                                    #
################################################################################

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
	
###############
# OUTPUT INFO #
###############

# output info to debug issues with this build
print_debugging_info

##################
# PREPARE APPDIR #
##################

# download the latest python-appimage release, which is an AppImage containing
# the core python3.7 runtime. We use this as a base for building our own python
# AppImage. We only have to add our code and depends to it.
wget --continue --output-document="/tmp/python.AppImage" "${PYTHON_APPIMAGE_URL}"
chmod +x /tmp/python.AppImage
/tmp/python.AppImage --appimage-extract
mv squashfs-root /tmp/kivy_appdir

/tmp/kivy_appdir/opt/python*/bin/python* -m pip install --upgrade -r requirements.txt

# add our code to the AppDir
rsync -a src /tmp/kivy_appdir/opt/

# output information about this build so the code can use it later in logs
cat > /tmp/kivy_appdir/opt/src/buskill_version.py <<EOF
BUSKILL_VERSION = {
 'GITHUB_REF': '${GITHUB_REF}',
 'GITHUB_SHA': '${GITHUB_SHA}',
 'SOURCE_DATE_EPOCH': '${SOURCE_DATE_EPOCH}',
}
EOF

# change AppRun so it executes our app
mv /tmp/kivy_appdir/AppRun /tmp/kivy_appdir/AppRun.orig
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

############
# THINNING #
############

# first print the pip packags installed before the thinning deletes pip
/tmp/kivy_appdir/opt/python*/bin/python* -m pip list

echo "INFO: Beginning AppDir thinning"

# remove some unnecessary items from the AppDir to reduce the AppImage size

unnecessary="__pycache__ pip pygments docutils setuptools chardet urllib3 elftools pkg_resources idna garden kivy-examples requests"
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

# download the latest stable release of appimagetool
pushd /tmp
wget --continue --output-document="/tmp/appimagetool.AppImage" https://github.com/AppImage/AppImageKit/releases/download/12/appimagetool-x86_64.AppImage
chmod +x /tmp/appimagetool.AppImage

# The latest stable appimagetool uses an old version of mksquashfs (v4.3),
# which does not support reproducable builds. Here we download the latest
# squashfs-tools (v4.4) and hack appimagetools to use it. For more info, see:
#  * https://github.com/BusKill/buskill-app/issues/3
wget --continue --output-document="squashfs4.4.tar.gz" "https://sourceforge.net/projects/squashfs/files/squashfs/squashfs4.4/squashfs4.4.tar.gz/download"

tar -xzvf squashfs4.4.tar.gz
pushd squashfs4.4/squashfs-tools
sudo apt-get install zlib1g-dev make
make
popd


/tmp/appimagetool.AppImage --appimage-extract
mv /tmp/squashfs-root /tmp/appimagetool_appdir
mv /tmp/appimagetool_appdir/usr/lib/appimagekit/mksquashfs /tmp/appimagetool_appdir/usr/lib/appimagekit/mksquashfs.orig

cat > /tmp/appimagetool_appdir/usr/lib/appimagekit/mksquashfs <<EOF
#!/usr/bin/sh

export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH}"

# the new version of mksquashfs no longer supports the '-mkfs-fixed-time'
# argument, so we remove it
args=\$(echo "\$@" | sed -e 's/-mkfs-fixed-time 0//')
/tmp/squashfs4.4/squashfs-tools/mksquashfs \$args
EOF

chmod +x /tmp/appimagetool_appdir/usr/lib/appimagekit/mksquashfs

# TODO: remove me
/tmp/appimagetool_appdir/usr/lib/appimagekit/mksquashfs -version
ls -lah /tmp/appimagetool_appdir/usr/lib/appimagekit/
cat /tmp/appimagetool_appdir/usr/lib/appimagekit/mksquashfs
ls -lah /tmp/squashfs4.4/squashfs-tools/

popd # leave /tmp

##################
# BUILD APPIMAGE #
##################

# create the dist dir for our result to be uploaded as an artifact
# note tha gitlab will only accept artifacts that are in the build dir (cwd)
mkdir dist

# create the AppImage from kivy AppDir
/tmp/appimagetool_appdir/AppRun --no-appstream "/tmp/kivy_appdir" "dist/${APP_NAME}.AppImage"

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
