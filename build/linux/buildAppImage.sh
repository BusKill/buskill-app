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
 'GITHUB_RUN_ID': '${GITHUB_RUN_ID}',
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

unnecessary="pip pygments docutils setuptools chardet urllib3 elftools pkg_resources idna garden kivy-examples requests"
for item in $(echo "${unnecessary}"); do

	paths=`find /tmp/kivy_appdir -iname "*${item}*"`

	for path in $(echo "${paths}"); do
		if [ -e ]; then
			echo "INFO: deleting $path "
			rm -rf "${path}"
		fi
	done

done

##################
# BUILD APPIMAGE #
##################

# create the AppImage from kivy AppDir
wget --continue --output-document="/tmp/appimagetool.AppImage" https://github.com/AppImage/AppImageKit/releases/download/12/appimagetool-x86_64.AppImage
chmod +x /tmp/appimagetool.AppImage

# create the dist dir for our result to be uploaded as an artifact
# note tha gitlab will only accept artifacts that are in the build dir (cwd)
mkdir dist
/tmp/appimagetool.AppImage --no-appstream "/tmp/kivy_appdir" "dist/${APP_NAME}.AppImage"

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
