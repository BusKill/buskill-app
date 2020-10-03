#!/bin/bash
set -x
################################################################################
# File:    linux/debianWrapper.sh
# Purpose: Executes the linux build script in an Ubuntu docker container so
#          the resulting build is reproducible with our GitHub shared runner's
#          build, which runs in Ubuntu. See also:
#
#          * https://docs.github.com/en/actions/reference/specifications-for-github-hosted-runners#supported-runners-and-hardware-resources
#
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-10-03
# Updated: 2020-10-03
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

###################
# INSTALL DEPENDS #
###################

# TODO: add distro detection and commands for other package managers, if needed
#       currently this has only been tested on Debian 10

sudo apt-get -y install docker.io

##################
# DOWNLOAD IMAGE #
##################

# At the time of writing, Docker Content Trust is 100% security theater without
# explicitly adding the root public keys to the $HOME/.docker/trust/ directory
#
#  * https://github.com/BusKill/buskill-app/issues/6#issuecomment-700050760
#  * https://security.stackexchange.com/questions/238529/how-to-list-all-of-the-known-root-keys-in-docker-docker-content-trust
#  * https://github.com/docker/cli/issues/2752

find /root/.docker/trust -type f -exec sha256sum '{}' \;
mkdir -p /root/.docker/trust/tuf/
cp -r build/deps/docker.io /root/.docker/trust/tuf/
find /root/.docker/trust -type f -exec sha256sum '{}' \;

output=`sudo DOCKER_CONTENT_TRUST=1 docker -D pull debian:stable-slim`

# did docker download a root key and dumbly trust it, bypassing all security?
echo $output | grep "200 when retrieving metadata for root"
if [[ $? -eq 0 ]]; then
	echo "ERROR: Failed to pin root signing key for debian image"
	exit 1
fi

##############
# DOCKER RUN #
##############

sudo docker run --rm -it --cap-add "NET_ADMIN" -v "`pwd`:/root/buskill-app" -v "/tmp/kivy_appdir:/tmp/kivy_appdir" debian:stable-slim /bin/bash -c "cd /root/buskill-app && build/linux/buildAppImage.sh"

# clean exit
exit 0
