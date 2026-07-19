.. _documentation:

Documentation
=============

This section documents how to update and build the documentation

Continuous Documentation
------------------------

The BusKill project treats documentation-as-code. It is versioned, managed with ``git``, and automatically built and released with our `CI/CD GitHub Actions workflows <https://github.com/BusKill/buskill-app/blob/master/.github/workflows/docs_pages_workflow.yml>`_.

Our documentation is written in `reStructuredText (reST) <https://en.wikipedia.org/wiki/ReStructuredText>`_ and built using `sphinx <https://www.sphinx-doc.org/en/master/>`_ with the `Read The Docs theme <https://github.com/readthedocs/sphinx_rtd_theme>`_. This has the following benefits:

#. reST is human-readable plaintext. It plays nice with a VCS (like ``git``).

   a. Plaintext is easier to review for PRs, making malicious PRs easier to detect.
   b. It's not necessary to build in order to read. The cryptographically-signed git commit sources can be read directly.
   c. Our documentation gets versioned exactly matching our code's release branches.

#. It's trivial for Sphinx to export to `multiple formats <https://www.sphinx-doc.org/en/master/usage/builders/index.html>`_, such as HTML, PDF, EPUB, etc.

#. reST is much more powerful than other human-readable markups.

   a. We can define our own `extensions using python <https://www.sphinx-doc.org/en/master/development/tutorials/helloworld.html>`_ to do complex logic like `converting LibreOffice spreadsheets with calculations into tables <https://stackoverflow.com/questions/62682095/how-to-add-a-spreadsheet-in-read-the-docs>`_

#. Sphinx has built-in support for documenting python sourcecode using `autodoc <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_

Updating
--------

If you'd like to update this documentation, you can `fork <https://docs.github.com/en/github/getting-started-with-github/fork-a-repo>`_ our `repo <https://github.com/buskill/buskill-app>`_, edit the files as-needed in the `docs directory <https://github.com/BusKill/buskill-app/tree/master/docs>`_, and `submit a PR <https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork>`_.

To know which file to edit, click the ``Edit on GitHub`` link on the top-right of the page you wish to edit.

.. _documentation_building:

Building
--------

You can build our documentation on Debian 10 using the following commands

::

  sudo apt-get update
  sudo apt-get -y install git firefox-esr python3-sphinx python3-sphinx-rtd-theme

  git clone https://github.com/BusKill/buskill-app.git
  cd buskill-app/docs

  make clean
  make html

After executing the above commands, you should have a new ``docs/_build/html/`` directory. You can open your locally-built documentation in firefox by executing

::

  firefox-esr docs/_build/html/index.html
