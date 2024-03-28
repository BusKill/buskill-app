.. _security_infrastructure:

Don't trust the infrastructure
==============================

This website is hosted on `GitHub Pages <https://pages.github.com/>`_. Therefore, it is largely outside of our control.

We don’t consider this a problem, however, since we explicitly distrust the infrastructure. For this reason, we don’t think that anyone should place undue trust in the live version of this site on the Web.

Instead, if you want to obtain your own, trustworthy copy of this website in a secure way, you should clone our `buskill-app repo <https://github.com/buskill/buskill-app>`_, verify the PGP signatures on the commits and/or tags, then either :ref:`render the site on your local machine <documentation_building>` or simply read the source.

We intentionally write our documentation in ReStructuredText so it's readable as plain text for this very reason. We’ve gone to special effort to set all of this up so that no one has to trust the infrastructure and so that the contents of this website are maximally available and accessible.

We believe the best solution is not to attempt to make the infrastructure trustworthy, but instead to concentrate on solutions that obviate the need to do so. We believe that many attempts to make the infrastructure appear trustworthy actually provide only the illusion of security and are ultimately a disservice to real users. Since we don’t want to encourage or endorse this, we make our distrust of the infrastructure explicit.

.. note::

  This was adapted from QubesOS's `distrust the infrastructure <https://www.qubes-os.org/faq/#what-does-it-mean-to-distrust-the-infrastructure>`_ philosophy.
