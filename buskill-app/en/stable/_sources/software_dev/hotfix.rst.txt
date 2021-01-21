.. _hotfix:

Hotfix Workflow
===============

This section will describe how to create a hotfix to a previous release.

Determine Version Number
------------------------

The first thing you must do before creating a hotfix to a previous release is determine the new (`semantic <https://semver.org/>`_) version number.

In this example, we'll be using ``v3.2.1``. That's

 * a ``MAJOR`` version ``3``,
 * a ``MINOR`` version ``2``, and 
 * a ``PATCH`` version ``1``

For this workflow, we assume that the previous release that we need to patch was ``v3.2.0``, and we'll be creating a hotfix ``v3.2.1``. The ``PATCH`` version must always be one higher than the previous release that we're patching.

::

	    v 3 . 2 . 1 ⭠ PATCH
	MAJOR ⮥   ⮤ MINOR

Create Hotfix Branch
---------------------

In our project, we only put production-ready stable code in the ``master`` branch. No commits should occur in ``master``.

The ``dev`` branch and feature-specific branches are branched-off from the ``dev`` branch or ``master`` directly.

Since your hotfix applies to an old release and there may have since been changes to ``dev`` or ``master`` that we don't want to backport just for the hotfix, we should create a hotfix-specific branch from the previous release branch.

::

	user@host:~/buskill-app$ git checkout -b v3.2.1 refs/heads/v3.2.0
	Switched to a new branch 'v3.2.1'
	userhost:~/buskill-app$ 

	user@host:~/buskill-app$ git push origin v3.2.1
	Total 0 (delta 0), reused 0 (delta 0)
	remote: 
	remote: Create a pull request for 'v3.2.1' on GitHub by visiting:
	remote:      https://github.com/BusKill/buskill-app/pull/new/v3.2.0
	remote: 
	To github.com:BusKill/buskill-app.git
 	* [new branch]      v3.2.1 -> v3.2.1
	user@host:~/buskill-app$ 

Finalize Release
----------------

After applying your patch to the new ``v3.2.1`` branch, make sure to also

#. Update CHANGELOG
#. Test
#. Update documentation

Then commit the changes and push to github. Do *not* merge the hotfix branch with any other branch.

::

	user@host:~/buskill-app/$ vim CHANGELOG
	user@host:~/buskill-app/$ git commit -am 'updated changelog for new release'
	user@host:~/buskill-app/$ git push
	...

Tag
---

Create a tag for the new hotfix release, and push that to github.com

::

	user@host:~/buskill-app$ git branch -l
	  dev
	  master
	  v3.2.0
	* v3.2.1
	user@host:~/buskill-app$

	user@host:~/buskill-app$ git tag v3.2.1

	user@host:~/buskill-app$ git push origin refs/tags/v3.2.1
	Total 0 (delta 0), reused 0 (delta 0)
	To github.com:BusKill/buskill-app.git
	 * [new tag]         v3.2.1 -> v3.2.1
	user@host:~/buskill-app$ 

Build, Sign, and Upload
-----------------------

To build, sign, and upload the hotfix release, follow the same steps in the :ref:`Release Workflow <release_build>` documentation.

.. _reproducible: https://github.com/BusKill/buskill-app/issues/3
