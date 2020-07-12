#!/bin/bash
set -x
################################################################################
# File:    updatePages.sh
# Purpose: Script that builds our documentation using sphinx and updates GitHub
#          Pages. This script is executed by:
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

export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)

################################################################################
#                                 MAIN BODY                                    #
################################################################################

###################
# INSTALL DEPENDS #
###################

apt-get update
apt-get -y install git python3-sphinx rsync

##############
# BUILD DOCS #
##############

# build our documentation with sphinx (see docs/conf.py)
# * https://www.sphinx-doc.org/en/master/usage/quickstart.html#running-the-build
make -C docs clean
make -C docs html

#######################
# Update GitHub Pages #
#######################

docroot=`mktemp -d`
pushd "${docroot}"

# don't bother maintaining history; just generate fresh
git init
git remote add origin "https://token@${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
git checkout -b gh-pages

# copy the resulting html pages built from sphinx above to our new git repo
rsync -av "docs/_build/html/" "${pagesSandbox}/"
git add .

# commit all the new files
msg="Updating Docs for commit ${GITHUB_SHA} made on `date -d"@${SOUCE_DATE_EPOCH}" --iso-8601=seconds` from ${GITHUB_REF}"
git commit -am "${msg}"

# overwrite the contents of the gh-pages branch on our github.com repo
git push origin gh-pages --force

##################
# CLEANUP & EXIT #
##################

# exit cleanly
exit 0
