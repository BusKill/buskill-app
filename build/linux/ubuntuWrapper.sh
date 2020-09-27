#!/bin/bash
set -x
################################################################################
# File:    linux/ubuntuWrapper.sh
# Purpose: Executes the linux build script in an Ubuntu docker container so
#          the resulting build is reproducible with our GitHub shared runner's
#          build, which runs in Ubuntu. See also:
#
#          * https://docs.github.com/en/actions/reference/specifications-for-github-hosted-runners#supported-runners-and-hardware-resources
#
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-09-24
# Updated: 2020-09-27
# Version: 0.2
################################################################################

#################
# SANITY CHECKS #
#################

# this script isn't robust enough
if [ ! -e "`pwd`/build/linux/buildAppImage.sh" ]; then
	echo "ERROR: This script should only be executed from the root of the github dir."
	exit 1
fi

###################
# INSTALL DEPENDS #
###################

# TODO: add distro detection and commands for other package managers, if needed
#       currently this has only been tested on Debian 10

sudo apt-get -y install docker.io
sudo docker pull ubuntu:18.04

##############
# DOCKER RUN #
##############

sudo docker run --rm -it --cap-add "NET_ADMIN" -v "`pwd`:/root/buskill-app" -v "/tmp/kivy_appdir:/tmp/kivy_appdir" ubuntu:18.04 /bin/bash -c "cd /root/buskill-app && build/linux/buildAppImage.sh"

# clean exit
exit 0
