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
# Updated: 2022-07-06
# Version: 0.3
################################################################################

############
# SETTINGS #
############

DOCKER_IMAGE_NAME='debian:bullseye-slim'

#################
# SANITY CHECKS #
#################

# this script isn't robust enough
if [ ! -e "`pwd`/build/linux/$(basename $0)" ]; then
	echo "ERROR: This script should only be executed from the root of the github dir."
	exit 1
fi

# re-run this as root if we're not already (needed for docker host stuff)
if [[ `whoami` != "root" ]]; then
        sudo ./build/linux/debianWrapper.sh || exit $?

        # this exits the parent process run by the user
        exit 0
fi

###################
# INSTALL DEPENDS #
###################

# TODO: add distro detection and commands for other package managers, if needed
#       currently this has only been tested on Debian 10

apt-get clean
apt-get -y install docker.io

##################
# DOWNLOAD IMAGE #
##################

# At the time of writing, Docker Content Trust is 100% security theater without
# explicitly adding the root public keys to the $HOME/.docker/trust/ directory
#
#  * https://github.com/BusKill/buskill-app/issues/6#issuecomment-700050760
#  * https://security.stackexchange.com/questions/238529/how-to-list-all-of-the-known-root-keys-in-docker-docker-content-trust
#  * https://github.com/docker/cli/issues/2752

find ${HOME}/.docker/trust -type f -exec sha256sum '{}' \;
mkdir -p ${HOME}/.docker/trust/tuf/
cp -r build/deps/docker.io ${HOME}/.docker/trust/tuf/
find ${HOME}/.docker/trust -type f -exec sha256sum '{}' \;

output=`DOCKER_CONTENT_TRUST=1 docker -D pull ${DOCKER_IMAGE_NAME} 2>&1`
#echo $output

# did docker download a root key and dumbly trust it, bypassing all security?
echo $output | grep "200 when retrieving metadata for root"
if [[ $? -eq 0 ]]; then
	echo "ERROR: Failed to pin root signing key for debian image"
	exit 1
fi

##############
# DOCKER RUN #
##############

# first cleanup the temp shared volume since this can't be done inside the
# docker container
rm -rf /tmp/kivy_appdir

docker run --rm --cap-add "NET_ADMIN" -v "`pwd`:/root/buskill-app" -v "/tmp/kivy_appdir:/tmp/kivy_appdir" ${DOCKER_IMAGE_NAME} /bin/bash -c "cd /root/buskill-app && build/linux/buildAppImage.sh"

###########
# CLEANUP #
###########

# make sure the resulting dist/ dir permissions let subsequent CI steps upload
# the build's artifacts
chown -R ${SUDO_USER} dist

exit 0
