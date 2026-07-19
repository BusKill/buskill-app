.. _verify_app_signature:

Verifying the Download
======================

Before executing anything downloaded from github.com, it's important to verify the cryptographic signature and integrity of the file.

.. warning::

	Note that github.com is not a website that we control, and :ref:`you should not trust <security_infrastructure>` it.

Before we can verify the authenticity of the BusKill app, it's necessary to download ``gpg`` and the BusKill release key. For information on how to obtain these dependencies, see :ref:`pgpkeys`.

Once the ``BusKill Releases Signing Key`` is in your ``gpg`` keyring, execute the following to verify the BusKill app downloaded from github.com

::

	user@host:~/Downloads$ ls
	buskill-linux-x86_64.v0.1.0.tar.bz2  SHA256SUMS  SHA256SUMS.asc
	user@host:~/Downloads$ 

	user@host:~/Downloads$ gpg --verify SHA256SUMS.asc 
	gpg: assuming signed data in 'SHA256SUMS'
	gpg: Signature made Sat 01 Aug 2020 02:05:32 PM +0545
	gpg:                using RSA key 798DC1101F3DEC428ADE124D68B8BCB0C5023905
	gpg: Good signature from "BusKill Releases Signing Key 2020.07 <releases@buskill.in>" [unknown]
	gpg: WARNING: This key is not certified with a trusted signature!
	gpg:          There is no indication that the signature belongs to the owner.
	Primary key fingerprint: E0AF FF57 DC00 FBE0 5635  8761 4AE2 1E19 36CE 786A
	     Subkey fingerprint: 798D C110 1F3D EC42 8ADE  124D 68B8 BCB0 C502 3905
	user@host:~/Downloads$

	user@host:~/Downloads$ sha256sum --ignore-missing -c SHA256SUMS
	buskill-linux-x86_64.v0.1.0.tar.bz2: OK
	user@host:~/Downloads$ 
