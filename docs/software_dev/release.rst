.. _release:

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

In our project, we only put production-ready stable code in the `master` branch. No commits should occur in `master`. Most commits should be made in the `dev` branch (or in a feature-specific branch, then merged into `dev`).

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

Finalize Release
----------------

At this point, all of your features for the new release should already be finished, but there are some release-specific changes that may need to be committed, such as:

#. Updating CHANGELOG
#. Testing & minor patches
#. Updating documentation

Test
----

Before release, thoroughly test the code in your new release branch and commit directly to this branch.

When testing is finished, merge all the commits into both the `master` and `dev` branches.

::

	user@host:~/buskill-app$ git branch -l
	  dev
	  master
	* v3.2.0

	user@host:~/buskill-app$ git checkout dev
	Switched to branch 'dev'

	user@host:~/buskill-app$ git pull origin dev
	From github.com:BusKill/buskill-app
	 * branch            dev        -> FETCH_HEAD
	Already up to date.
	user@host:~/buskill-app$ git merge v3.2.0
	Updating f9e692a..3c1a6d5
	Fast-forward
	 docs/software_dev/index.rst   |  2 +-
	 docs/software_dev/release.rst | 54 +++++++++++++++++++++++++++++++++++++++++++
	 docs/software_dev/repo.rst    |  6 -----
	 3 files changed, 55 insertions(+), 7 deletions(-)
	 create mode 100644 docs/software_dev/release.rst
	 delete mode 100644 docs/software_dev/repo.rst
	user@host:~/buskill-app$ git checkout master
	Switched to branch 'master'
	Your branch is up to date with 'origin/master'.

	user@host:~/buskill-app$ git pull origin master
	From github.com:BusKill/buskill-app
	 * branch            master     -> FETCH_HEAD
	Already up to date.

	user@host:~/buskill-app$ git merge v3.2.0
	Updating ab223f3..3c1a6d5
	Fast-forward
	 docs/_extensions/affiliatelinks.py  |  66 ++++++++++++++++++++++++++++
	 docs/attribution.rst                |   1 +
	 docs/conf.py                        |  13 ++++++
	 docs/contributing.rst               |   3 +-
	 docs/hardware_dev/assembly.rst      |   7 +++
	 docs/hardware_dev/bom.rst           |  83 ++++++++++++++++++++++++++++++++++++
	 docs/hardware_dev/index.rst         |   7 ++-
	 docs/images/buskill_cable_usb_a.jpg | Bin 0 -> 457480 bytes
	 docs/index.rst                      |   7 +++
	 docs/software_dev/index.rst         |   2 +-
	 docs/software_dev/release.rst       |  54 +++++++++++++++++++++++
	 docs/software_dev/repo.rst          |   6 ---
	 12 files changed, 239 insertions(+), 10 deletions(-)
	 create mode 100644 docs/_extensions/affiliatelinks.py
	 create mode 100644 docs/hardware_dev/assembly.rst
	 create mode 100644 docs/hardware_dev/bom.rst
	 create mode 100644 docs/images/buskill_cable_usb_a.jpg
	 create mode 100644 docs/software_dev/release.rst
	 delete mode 100644 docs/software_dev/repo.rst

	user@host:~/buskill-app$ git checkout v3.2.0
	Switched to branch 'v3.2.0'

	user@host:~/buskill-app$ git push
	Enumerating objects: 10, done.
	Counting objects: 100% (10/10), done.
	Delta compression using up to 4 threads
	Compressing objects: 100% (6/6), done.
	Writing objects: 100% (6/6), 2.10 KiB | 63.00 KiB/s, done.
	Total 6 (delta 3), reused 0 (delta 0)
	remote: Resolving deltas: 100% (3/3), completed with 3 local objects.
	To github.com:BusKill/buskill-app.git
	   f9e692a..3c1a6d5  dev -> dev
	   ab223f3..3c1a6d5  master -> master
	   f9e692a..3c1a6d5  v3.2.0 -> v3.2.0

	user@host:~/buskill-app$ 

Tag
---

After you've merged your release branch into the `master` branch, create a tag for the new release in the `master` branch, and push that to github.com

::

	user@host:~/buskill-app$ git checkout master
	Switched to branch 'master'
	Your branch is up to date with 'origin/master'.

	user@host:~/buskill-app$ git tag v0.1.0

	user@host:~/buskill-app$ git push origin refs/tags/v0.1.0
	Total 0 (delta 0), reused 0 (delta 0)
	To github.com:BusKill/buskill-app.git
	 * [new tag]         v0.1.0 -> v0.1.0

	user@host:~/buskill-app$ 

Build & Sign
------------

For Linux, use the `build script <https://github.com/BusKill/buskill-app/blob/master/build/linux/buildAppImage.sh>`_ to build the new release locally on your machine in a fresh linux VM as root. Get the sha256 checksum of the new AppImage and confirm that it matches the AppImage built by GitHub's CI process. If it doesn't, don't proceed with signing it. Our Linux releases should be fully reproducible_.

::

user@disp215:~$ 
user@disp215:~$ sudo su -
root@disp215:~#	

root@disp215:~# git clone https://github.com/BusKill/buskill-app.git
Cloning into 'buskill-app'...
...
Checking out files: 100% (120/120), done.
root@disp215:~# 

root@disp215:~# cd buskill-app/
root@disp215:~/buskill-app# build/linux/buildAppImage.sh 
...
root@disp215:~/buskill-app# 

root@disp215:~/buskill-app# sha256sum dist/buskill.AppImage
663ee5275256760a6dc04736f7211bd7482708f4f82c451b78733df442adaa37  dist/buskill.AppImage
root@disp215:~/buskill-app# 

root@disp215:~/buskill-app# cd ..
root@disp215:~# wget https://github.com/BusKill/buskill-app/releases/download/<epoch_seconds>/buskill-linux-x86_64.<epoch_seconds>.tar.bz2
...
root@disp215:~# tar -xjf buskill-linux-x86_64.181376356.tar.bz2 
root@disp215:~# sha256sum dist/buskill.AppImage 
292984aa32315bced99e88e9585a411cb341eb74166350e0fec2f80ba0bb672a  dist/buskill.AppImage
root@disp215:~# 






For Windows & MacOS, there is an `upstream issue with reproducibility in PyInstaller <https://github.com/BusKill/buskill-app/issues/3>`_, so we have to choose to trust our local build or the GitHub CI build.

TODO: Steps to preform when releasing a new version (build/test/download/checksum diff/sign/upload, create new branch for dev, update build depends)

.. _reproducible: https://github.com/BusKill/buskill-app/issues/3
