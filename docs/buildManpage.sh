#!/bin/bash
set -x
################################################################################
# File:    buildManpage.sh
# Purpose: Script that converts manpage.rst (in reStructuredText format) into
#          buskill.1 (in groff format)
#
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2022-12-12
# Updated: 2022-12-12
# Version: 0.1
################################################################################

################################################################################
#                                  SETTINGS                                    #
################################################################################

# n/a

################################################################################
#                                 MAIN BODY                                    #
################################################################################

#################
# SANITY CHECKS #
#################

# this script isn't robust enough
if [ ! -e "`pwd`/docs/$(basename $0)" ]; then
	echo "ERROR: This script should only be executed from the root of the github dir."
	exit 1
fi

###################
# INSTALL DEPENDS #
###################

apt-get update
apt-get -y install pandoc

#####################
# DECLARE VARIABLES #
#####################

PANDOC=`which pandoc`

pwd
env
ls -lah
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)
DATE=$(date "+%b %Y" --date="@${SOURCE_DATE_EPOCH}")
HEADER="Laptop Kill Cord"

# make a new temp dir which will be our GitHub Pages docroot
docroot=`mktemp -d`

#################
# BUILD MANPAGE #
#################

${PANDOC} -s -t man --variable header="${HEADER}" --variable date="${DATE}" --variable footer="${FOOTER}" docs/software_usr/manpage.rst -o "docs/buskill.1"

##################
# CLEANUP & EXIT #
##################

# exit cleanly
exit 0
