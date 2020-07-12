#!/bin/bash
set -x
################################################################################
# File:    signRelease.sh
# Purpose: Script that signs builds our documentation using sphinx and updates
#          GitHub Pages. This script is executed by:
#            .github/workflows/docs_pages_workflow.yml
#
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-07-13
# Updated: 2020-07-13
# Version: 0.1
################################################################################

################################################################################
#                                  SETTINGS                                    #
################################################################################

# n/a

################################################################################
#                                 MAIN BODY                                    #
################################################################################

###################
# INSTALL DEPENDS #
###################

apt-get update
apt-get -y install git python3-sphinx

##############
# BUILD DOCS #
##############

sandbox=`mktemp -d`
pushd "${tmpDir}"

# TODO clone repo using env vars
env

##################
# CLEANUP & EXIT #
##################

# exit cleanly
exit 0
