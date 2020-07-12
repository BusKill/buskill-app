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

# n/a

################################################################################
#                                 MAIN BODY                                    #
################################################################################

###################
# INSTALL DEPENDS #
###################

apt-get update
apt-get -y install git python3-sphinx rsync

#####################
# DECLARE VARIABLES #
#####################

pwd
ls -lah
ls -lah
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)

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

git config --global user.name "${GITHUB_ACTOR}"
git config --global user.email "${GITHUB_ACTOR}@users.noreply.github.com"

docroot=`mktemp -d`
rsync -av "docs/_build/html/" "${docroot}/buskill-app/"

pushd "${docroot}"

# don't bother maintaining history; just generate fresh
git init
git remote add deploy "https://token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
git checkout -b gh-pages

# Add CNAME - this is required for GitHub to know what our custom domain is
echo "docs.buskill.in" > CNAME

# add redirect (for now) since I want repo-specific docs dirs, but we only have one so far
cat >> index.html <<EOF
<!DOCTYPE html>
<html>
   <head>
      <title>BusKill Docs</title>
      <meta http-equiv = "refresh" content="0; url='/buskill-app/'" />
   </head>
   <body>
      <p>Please wait while you're redirected to our <a href="/buskill-app/">buskill-app documentation page</a>.</p>
   </body>
</html>
EOF

# Add README
cat >> README.md <<EOF
# GitHub Pages Cache

Nothing to see here. The contents of this branch are essentially a cache that's not intended to be viewed on github.com.

You can view the actual documentation as it's intended to be viewed at [https://docs.buskill.in/](https://docs.buskill.in/)

If you're looking to update our documentation, check the relevant development branch's ['docs' dir](https://github.com/BusKill/buskill-app/tree/master/docs).
EOF

# copy the resulting html pages built from sphinx above to our new git repo
git add .

# commit all the new files
msg="Updating Docs for commit ${GITHUB_SHA} made on `date -d"@${SOURCE_DATE_EPOCH}" --iso-8601=seconds` from ${GITHUB_REF}"
git commit -am "${msg}"

# overwrite the contents of the gh-pages branch on our github.com repo
git push deploy gh-pages --force

popd # return to main repo sandbox root

##################
# CLEANUP & EXIT #
##################

# exit cleanly
exit 0
