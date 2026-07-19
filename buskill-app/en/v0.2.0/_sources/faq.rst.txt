.. _faq:

Frequently Asked Questions
==========================

.. _faq_triggers:

Q: What is BusKill?
-------------------

BusKill is the world's first laptop `kill cord <https://en.wikipedia.org/wiki/Kill_cord>`_. It's a hardware `Dead Man's Switch <https://en.wikipedia.org/wiki/Dead_man%27s_switch>`_ that can trigger your laptop to lock, shutdown, or self-destruct if your machine is physically separated from you.

For a more detailed explanation on what BusKill is and who it's designed for, see :ref:`what`

.. _faq_buy:

Q: Where can I **buy** a BusKill cable?
---------------------------------------

You can `purchase a BusKill cable <https://buskill.in/buy>`_ from our website.

Q: What actions can I trigger with BusKill?
-------------------------------------------

Anything scriptable! Currently the BusKill App supports locking your screen and shutting down your computer.

.. _faq_selfdestruct:

Q: Self-destruct?!? Will this brick my computer?
------------------------------------------------

No. Advanced users can add triggers that wipe RAM and encryption keys. This self-destruct sequence will make all of the data previously stored on a machine with Full Disk Encryption permanently useless. Note that this "self-destruct" sequence destroys the data only, not the hardware.

**This self-destruct trigger is not included in BusKill by default.** So for most users, the worst that can happen is your machine powers off. No data loss. No fried hardware.

.. _faq_false_positives:

Q: What about false-positives?
--------------------------------------------------------------------------------------------
BusKill's breakaway connector uses strong magnets that decreases the risk of false-positives.

That said, it *is* designed to breakaway, so if you accidentally trigger BusKill (by, say, standing up to get a cup of coffee without disarming BusKill), then the worst that can happen (if you're using the BusKill app without manually adding ``auxilary triggers``) is that your computer will shutdown.

Here's some tips to avoid false-positives:

 #. When using BusKill, work on a sturdy table with a comfortable chair.
 #. Avoid moving your laptop after arming BusKill in the app.
 #. The first few days, limit yourself to just the ``lock screen`` trigger to avoid loosing your work as you get used to disarming BusKill before taking toilet breaks.

See also :ref:`faq_bluetooth`

.. _faq_interdiction:

Q: What about interdiction?
--------------------------------------------------------------------------------------------

Unfettered physical access can defeat most security, and installation of malicious software or hardware implants is a real risk for shipping.

We don't consider hologram stickers or tamper-evident tape/crisps/glitter to be sufficient solutions to supply-chain security. Rather, the solution to these attacks is to build open-source, disassembleable, and easily inspectable hardware whose integrity can be validated without damaging the device and without sophisticated technology.

Fortunately, the requirements for BusKill's hardware components are simple, making integrity verification relatively easy.

If you'd like to help BusKill make our open-source cable more resistant to interdiction attacks, please `contact us <https://buskill.in/contact/>`_ about designing :ref:`verifiable hardware components <wishlist_hardware>`.

.. _faq_clone:

Q: Could an attacker clone my BusKill drive and quickly insert it before stealing my laptop?
--------------------------------------------------------------------------------------------
No. Even if an exact replica was inserted, BusKill will still be triggered if it's disconnected.

.. _faq_2fa:

Q: But I'm using 2FA and my OS has FDE with AES 256 and a 20-word passphrase.
-----------------------------------------------------------------------------

That's good! But it won't protect you if a thief snatch-and-runs with your laptop *after* you've authenticated.

The only way to defend against this sort of attack is by using a Dead Man Switch to detect that you've been replaced at the helm, such as BusKill.

.. _faq_bluetooth:

Q: But bluetooth...
-------------------

Using a radio-based Dead Man Switch introduces complexity, delays, and an increased vector of attack. BusKill is a simple hardware kill cord and is therefore more secure than any wireless solution.

.. _faq_follow:


Q: How can I get updates about BusKill?
---------------------------------------

You can `signup for our BusKill email newsletter <https://www.buskill.in/#newsletter>`_ or follow us on any of the following social media profiles:

* Twitter `@BusKillin <https://twitter.com/buskillin>`_
* Facebook `@BusKill.in <https://www.facebook.com/BusKill.in/>`_
* Mastodon `BusKillin@Mastodon.social <https://mastodon.social/@BusKillin>`_
* GitHub `BusKill <https://github.com/BusKill>`_
* YouTube `BusKill <https://www.youtube.com/channel/UC5Njxb027m2OmrocrH33oew/about>`_

.. _faq_support:

Q: My questions isn't listed. Where can I get support?
------------------------------------------------------

Please see :ref:`support`

