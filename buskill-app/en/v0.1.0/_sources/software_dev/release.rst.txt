.. _release:

Release Workflow
================

This section will describe how to create a new release.

Determine Version Number
------------------------

The first thing you must do before creating a new release is determine the new (`semantic <https://semver.org/>`_) version number.

In this example, we'll be using ``v3.2.0``. That's a ``MAJOR`` version ``3`` and ``MINOR`` version ``2``. The ``PATCH`` version is ``0``, and it should only be incremented for hotfixes to previous releases, which is a distinct workflow from what's documented here.

::

	v3.2.0

Create Release Branch
---------------------

In our project, we only put production-ready stable code in the ``master`` branch. No commits should occur in ``master``. Most commits should be made in the ``dev`` branch (or in a feature-specific branch, then merged into ``dev``).

After a set of features to be included in your new release are finished, create a new release branch from the ``dev`` branch. Push this new branch to github.com

::

	user@host:~/buskill-app$ git checkout dev
	Switched to branch 'dev'
	user@host:~/buskill-app$ git checkout -b v3.2.0
	Switched to a new branch 'v3.2.0'
	user@host:~/buskill-app$ 
	user@host:~/buskill-app$ git push origin v3.2.0
	Total 0 (delta 0), reused 0 (delta 0)
	remote: 
	remote: Create a pull request for 'v3.2.0' on GitHub by visiting:
	remote:      https://github.com/BusKill/buskill-app/pull/new/v3.2.0
	remote: 
	To github.com:BusKill/buskill-app.git
 	* [new branch]      v3.2.0 -> v3.2.0
	user@host:~/buskill-app$ 

Finalize Release
----------------

At this point, all of your features for the new release should already be finished, but there are some release-specific changes that may need to be committed, such as:

#. Updating CHANGELOG
#. Testing & minor patches
#. Updating documentation

::

	user@host:~/buskill-app/$ vim CHANGELOG
	user@host:~/buskill-app/$ git commit -am 'updated changelog for new release'
	user@host:~/buskill-app/$ 

Test
----

Before release, thoroughly test the code in your new release branch and commit directly to this branch.

When testing is finished, merge all the commits into both the ``master`` and ``dev`` branches.

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

After you've merged your release branch into the ``master`` branch, create a tag for the new release in the ``master`` branch, and push that to github.com

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

When downloading the AppImage from the repo's GitHub releases page, make sure the commits and branches exactly match your local build, else the checksum will differ because the contents of ``buskill_version.py`` will have a distinct ``GITHUB_REF``, ``GITHUB_SHA``, and ``SOURCE_DATE_EPOCH``.

::

	user@disp2781:~$ 
	user@disp2781:~$ sudo su -
	root@disp2781:~#	
 	
	root@disp2781:~# git clone --single-branch --branch v3.2.0 https://github.com/BusKill/buskill-app.git
	Cloning into 'buskill-app'...
	remote: Enumerating objects: 21, done.
	...
	root@disp2781:~# cd buskill-app
	root@disp2781:~/buskill-app# git branch -l
	* v3.2.0
	root@disp2781:~/buskill-app# 
	
	root@disp2781:~/buskill-app# build/linux/buildAppImage.sh 
	...
	root@disp2781:~/buskill-app# 
	
	root@disp2781:~/buskill-app# sha256sum dist/buskill.AppImage
	66ebab6c980d49d20526a184981ba36b34bdc18dea40a5b2ff995b281eebfe9d  dist/buskill.AppImage
	root@disp2781:~/buskill-app# 
	
	root@disp2781:~/buskill-app# cd ..
	root@disp2781:~# wget https://github.com/BusKill/buskill-app/releases/download/<epoch_seconds>_linux/buskill-linux-x86_64.<epoch_seconds>.tar.bz2
	...
	root@disp2781:~# tar -xjf buskill-linux-x86_64.181376356.tar.bz2 
	root@disp2781:~# sha256sum dist/buskill.AppImage 
	66ebab6c980d49d20526a184981ba36b34bdc18dea40a5b2ff995b281eebfe9d  dist/buskill.AppImage
	root@disp2781:~# 

.. note::

	For Windows & MacOS, there is an `upstream issue with reproducibility in PyInstaller <https://github.com/BusKill/buskill-app/issues/3>`_, so we have to choose to trust our local build or the GitHub CI build.

After verifying the reproducibility of the Linux build, download the Windows and MacOS builds from the corresponding GitHub release and verify their pre-release signatures.

::

	root@disp2781:~# wget https://github.com/BusKill/buskill-app/releases/download/<epoch_seconds>_windows/buskill-windows-x86_64.<epoch_seconds>.zip
	...
	root@disp2781:~# curl --location --remote-name https://github.com/BusKill/buskill-app/releases/download/<epoch_seconds>_windows/SHA256SUMS
	...
	root@disp2781:~# curl --location --remote-name https://github.com/BusKill/buskill-app/releases/download/<epoch_seconds>_windows/SHA256SUMS.asc
	...
	root@disp2781:~# gpg --verify SHA256SUMS.asc
	gpg: Signature made Fri 31 Jul 2020 03:43:43 PM +0545
	gpg:                using RSA key 0B90809464D7B7A50E1871DE7DE9F38ADB5B1E8A
	gpg: Good signature from "BusKill Pre-Releases Signing Key 2020.07 <pre-releases@buskill.in>" [unknown]
	gpg: WARNING: This key is not certified with a trusted signature!
	gpg:          There is no indication that the signature belongs to the owner.
	Primary key fingerprint: 713D 4A49 60EE 849B AE3B  41BA BE75 DB07 E34A FBC1
	     Subkey fingerprint: 0B90 8094 64D7 B7A5 0E18  71DE 7DE9 F38A DB5B 1E8A
	gpg: WARNING: not a detached signature; file 'SHA256SUMS' was NOT verified!
	root@disp2781:~# sha256sum -c SHA256SUMS
	buskill-windows-x86_64.189828725.zip: OK
	root@disp2781:~# 

	root@disp2781:~# wget https://github.com/BusKill/buskill-app/releases/download/<epoch_seconds>_mac/buskill-mac-x86_64.<epoch_seconds>.tar.bz2
	...
	root@disp2781:~# curl --location --remote-name https://github.com/BusKill/buskill-app/releases/download/<epoch_seconds>_mac/SHA256SUMS
	...
	root@disp2781:~# curl --location --remote-name https://github.com/BusKill/buskill-app/releases/download/<epoch_seconds>_mac/SHA256SUMS.asc
	...
	root@disp2781:~# gpg --verify SHA256SUMS.asc 
	gpg: Signature made Fri 31 Jul 2020 03:43:43 PM +0545
	gpg:                using RSA key 0B90809464D7B7A50E1871DE7DE9F38ADB5B1E8A
	gpg: Good signature from "BusKill Pre-Releases Signing Key 2020.07 <pre-releases@buskill.in>" [unknown]
	gpg: WARNING: This key is not certified with a trusted signature!
	gpg:          There is no indication that the signature belongs to the owner.
	Primary key fingerprint: 713D 4A49 60EE 849B AE3B  41BA BE75 DB07 E34A FBC1
	     Subkey fingerprint: 0B90 8094 64D7 B7A5 0E18  71DE 7DE9 F38A DB5B 1E8A
	gpg: WARNING: not a detached signature; file 'SHA256SUMS' was NOT verified!
	root@disp2781:~# sha256sum -c SHA256SUMS
	buskill-mac-x86_64.189828725.tar.bz2: OK
	root@disp2781:~# 


Once you've verified the integrity of all three compressed archives, move them to your dragon-protected basement-safe laptop, rename them, generate a new checksum file with all three platforms' releases, and sign it with the gpg release key.

::

	user@vault:~$ ls
	buskill-linux-x86_64.189828725.tar.bz2  buskill-windows-x86_64.189828725.zip
	buskill-mac-x86_64.189828725.tar.bz2
	user@vault:~$ mv buskill-linux-x86_64.189828725.tar.bz2 buskill-linux-x86_64.v0.1.0.tar.bz2 
	user@vault:~$ mv buskill-windows-x86_64.189828725.zip buskill-windows-x86_64.v0.1.0.zip 
	user@vault:~$ mv buskill-mac-x86_64.189828725.tar.bz2 buskill-mac-x86_64.v0.1.0.tar.bz2 
	user@vault:~$ ls
	buskill-linux-x86_64.v0.1.0.tar.bz2  buskill-windows-x86_64.v0.1.0.zip
	buskill-mac-x86_64.v0.1.0.tar.bz2
	user@vault:~$ 
	user@vault:~$ sha256sum * > SHA256SUMS
	user@vault:~$ gpg --default-key 'E0AF FF57 DC00 FBE0 5635  8761 4AE2 1E19 36CE 786A' --armor -b SHA256SUMS
	gpg: using "E0AF FF57 DC00 FBE0 5635  8761 4AE2 1E19 36CE 786A" as default secret key for signing
	user@vault:~$ ls
	buskill-linux-x86_64.v0.1.0.tar.bz2  SHA256SUMS
	buskill-mac-x86_64.v0.1.0.tar.bz2    SHA256SUMS.asc
	buskill-windows-x86_64.v0.1.0.zip
	user@vault:~$ 

Upload
------

Copy all of the above files off your airgapped machine.

Finally, upload the files to the tag's release using the github.com WUI

 * `https://github.com/BusKill/buskill-app/releases/tag/v3.2.0 <https://github.com/BusKill/buskill-app/releases/tag/v0.1.0>`_

.. _reproducible: https://github.com/BusKill/buskill-app/issues/3
