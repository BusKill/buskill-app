.. _pgpkeys:

PGP Keys
========

This page contains the official BusKill PGP keys and the keys of various developers for the `buskill-app <https://github.com/buskill/buskill-app/>`_ repo.

For more info, see:
 * https://www.buskill.in

.. warning::

  This documentation is hosted on GitHub Pages, and :ref:`you should not trust <security_infrastructure>` its contents.

  A wise user that's adding our keys to their keyring for the first-time would cross-validate the PGP fingerprint listed on this website against other sources, such as:
   * The `official BusKill project website <https://www.buskill.in/>`_
   * The `official BusKill mastodon account <https://mastodon.social/@buskillin>`_
   * The `KEYS file <keys_file_>`_ at the root of our GitHub repo
   * A popular `gpg keyserver <https://keys.openpgp.org/search?q=releases%40buskill.in>`_
   * Your `friends' keyrings <https://en.wikipedia.org/wiki/Web_of_trust>`_

Users
-----

To add the BusKill PGP keys and our developer's keys to your keyring, execute the following commands.

::

  wget https://raw.githubusercontent.com/BusKill/buskill-app/master/KEYS

  # validate the full fingerprint against other out-of-band sources first
  gpg --keyid-format long KEYS

As noted above, it's very important that you pause and do your due-diligence to verify that the key is in-fact our key before proceeding with the final ``--import`` command.

::

  # don't execute this until you've verified the fingerprint out-of-band
  gpg --import KEYS

Developers
----------

If you're a developer and would like to include your pgp key in our org's ``KEYS`` file, please execute the following commands

::

  gpg --list-keys --armor <your fingerprint>
  gpg --list-sigs <your fingerprint>
  gpg --export --armor <your fingerprint>

And then append the output to the `KEYS file <keys_file_>`_.

KEYS
----

Our repo's `KEYS file <keys_file_>`_ is shown below

.. literalinclude:: ../../KEYS

.. _keys_file: https://github.com/BusKill/buskill-app/blob/master/KEYS

