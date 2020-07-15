.. _pgpkeys:

PGP Keys
========

This page contains the official BusKill PGP keys and the keys of various developers for the `buskill-app <https://github.com/buskill/buskill-app/>`_ repo.

For more info, see:
 * https://www.buskill.in

.. warning::

  This documentation is hosted on GitHub Pages, and `you should not trust <https://www.qubes-os.org/faq/#should-i-trust-this-website>`_ its contents.

  A wise user that's adding our keys to their keyring for the first-time would cross-validate the PGP fingerprint listed on this website against other sources, such as:
   * The `official BusKill project website <https://www.buskill.in/>`_
   * The `official BusKill keybase account <https://keybase.io/buskill/>`_
   * The `official BusKill mastodon account <https://mastodon.social/@buskillin>`_
   * The `KEYS file <https://github.com/BusKill/buskill-app/blob/master/KEYS.md>`_ at the root of our GitHub repo
   * A popular `gpg keyserver <https://keys.openpgp.org/search?q=releases%40buskill.in>`_
   * Your `friends' keyrings <https://en.wikipedia.org/wiki/Web_of_trust>`_

Users
-----

To add the BusKill PGP keys and our developer's keys to your keyring, execute the following commands.

As noted above, it's very important that you pause and do your due-diligence to verify that the key is in-fact our key before proceeding with the final ``--import`` command.

::

  wget https://raw.githubusercontent.com/BusKill/buskill-app/master/KEYS

  # validate the full fingerprint against other out-of-band sources first
  gpg --keyid-format long KEYS

  gpg --import KEYS

Developers
----------

If you're a developer and would like to include your pgp key in our org's ``KEYS`` file, please execute the following commands

::

  gpg --list-keys --armor <your fingerprint>
  gpg --list-sigs <your fingerprint>
  gpg --export --armor <your fingerprint>

And then append the output to the `KEYS file <https://github.com/BusKill/buskill-app/blob/master/KEYS>`_.

KEYS
----

Our repo's `KEYS file <https://github.com/BusKill/buskill-app/blob/master/KEYS>`_ is shown below

.. literalinclude:: ../../KEYS
