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
# Updated: 2020-09-24
# Version: 0.1
################################################################################

#################
# SANITY CHECKS #
#################

# this script isn't robust enough
if [ ! -e "`pwd`/build/linux/buildAppImage.sh" ]; then
	echo "ERROR: This script should only be executed from the root of the github dir."
	exit 1
fi

##############
# DOCKER RUN #
##############

docker run --rm -it -v "`pwd`:/root/buskill-app" ubuntu:18.04 /bin/bash -c "cd /root/buskill-app && build/linux/buildAppImage.sh"

# clean exit
exit 0
