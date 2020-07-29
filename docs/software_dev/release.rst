.. _repo:

Release Workflow
================

This section will describe how to create a new release.

Determine Version Number
------------------------

The first thing you must do before creating a new release is determine the new (`semantic <https://semver.org/>`_) version number. In this example, we'll be using v3.2.0. That's a MAJOR version 3 and MINOR version 2. The PATCH version is 0, and it should only be incremented for patches to previous releases, which is a distinct workflow from what's documented here.

::

	v3.2.0

Create Release Branch
---------------------

In our project, we only put stable code in the `master` branch. No commits should occur in `master`. Most commits should be made in the `dev` branch (or in a feature-specific branch, then merged into `dev`).

After a set of features to be included in your new release are finished, create a new release branch from the `dev` branch. Push this new branch to github.com

::

	user@host:~/buskill-app/docs$ git checkout dev
	Switched to branch 'dev'
	user@host:~/buskill-app/docs$ git checkout -b v3.2.0
	Switched to a new branch 'v3.2.0'
	user@host:~/buskill-app/docs$ 
	user@buskill:~/sandbox/buskill-app/docs$ git push origin v3.2.0
	Total 0 (delta 0), reused 0 (delta 0)
	remote: 
	remote: Create a pull request for 'v3.2.0' on GitHub by visiting:
	remote:      https://github.com/BusKill/buskill-app/pull/new/v3.2.0
	remote: 
	To github.com:BusKill/buskill-app.git
 	* [new branch]      v3.2.0 -> v3.2.0
	user@host:~/buskill-app/docs$ 


Test
----

Before release, thoroughly test the code in your new release branch and commit directly to this branch.

When testing is finished, merge all the commits into both the `master` and `dev` branches.

Tag
---

Create a tag for the release 

TODO: Steps to preform when releasing a new version (build/test/download/checksum diff/sign/upload, create new branch for dev, update build depends)
