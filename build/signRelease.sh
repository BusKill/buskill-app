#!/bin/bash
set -x
################################################################################
# File:    signRelease.sh
# Purpose: Script that signs our pre-releases. This should be called by the
#          sign_workflow, which is triggered by the build script. This is kept
#          seperate from the build scripts so it doesn't have to be implemented
#          on multiple platforms.
#
#          * https://github.com/BusKill/buskill-app/issues/4
#
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-07-12
# Updated: 2020-07-12
# Version: 0.1
################################################################################

################################################################################
#                                  SETTINGS                                    #
################################################################################

# n/a

################################################################################
#                                 MAIN BODY                                    #
################################################################################

######################
# INPUT SANITIZATION #
######################

# our only input should consist of only numbers; per our assignment below, if
# it has a double-quote in it, it could become a vector for arbitrary command
# execution; both checks are necessary.
#if [[ '${{ contains( github.event.client_payload.release_id, '"') }}' == 'true' ]]; then
#	echo "ERROR: release_id absolutely cannot have a double-quote!"
#	exit 1
#fi
#RELEASE_ID="${{ github.event.client_payload.release_id }}"
#RELEASE_ID="${RELEASE_ID//[^0-9]}"

echo "RELEASE_ID:|${RELEASE_ID}|"
RELEASE_ID="${RELEASE_ID//[^0-9]}"
echo "RELEASE_ID:|${RELEASE_ID}|"
exit 0

###################
# INSTALL DEPENDS #
###################

apt-get update
apt-get -y install curl

###########################
# DOWNLOAD RELEASE ASSETS #
###########################

echo "RELEASE_ID:|${RELEASE_ID}|"

curl -i --header "authorization: Bearer ${GITHUB_TOKEN}" "https://api.github.com/repos/buskill/buskill-app/releases/${RELEASE_ID}"

##################
# CLEANUP & EXIT #
##################

# exit cleanly
exit 0
