![build](https://github.com/BusKill/buskill-app/workflows/build/badge.svg?branch=master)

# BusKill App

This is the codebase for our cross-platform (CLI and) GUI app for [BusKill](https://www.buskill.in). It works in Linux, Windows, and MacOS.

BusKill is a laptop kill cord that can trigger your computer to lock or shutdown when it's physically seperated from you.

<p align="center">
  <img src=".github-assets/busKill_demo.gif?raw=true" alt="BusKill Demo Video"/>
</p>

For more information on how to buy or build your own BusKill cable, see the [BusKill Website](https://www.buskill.in):

 * [https://www.buskill.in](https://www.buskill.in)

![](.github-assets/busKill_featuredImage.jpg)

# Install

You can download this app by visiting our this repo's [releases page](https://github.com/BusKill/buskill-app/releases) on github.

BusKill is packaged as a self-contained executable. It includes the python interpreter and all required dependencies. This allows the program to be easily executed as a portable app that is distributed on the BusKill usb drive itself.

TODO: signature verification

No installation is needed after download. After downloading and extracting the compressed archive, simply double-click or execute buskill from the command-line.

# Documentation

TODO. Sphinx?

# Building from source

TODO Add note about deterministic/reproducable builds.

The scripts used to build this app are platform-specific and must be executed on the target platform. In other words, you cannot build the app for MacOS on a Linux platform, you cannot build for Windows on MacOS, for Linux on Windows, etc.

From the root of this repo, simply execute the relevant build script from the [build](build) directory.

For example, the following commands will build the BusKill app on Linux:

```
git clone https://github.com/BusKill/buskill-app.git
cd buskill-app
build/linux/buildAppImage.sh 
```

# Security

TODO move to docs dir (Sphinx?) and include notes about hardware implant risks and integrity verification

This app was created for convenience, providing the user with an easy-to-use method of arming, disarming, and configuring BusKill with an intuitive GUI that "just works" on Linux, Windows, and MacOS.

Convenience is a trade-off that comes at a cost of reduced security. Using this app requires your computer to not only run hundreds of lines of our code, but also thousands of lines of code from dependant libraries.

The most secure way to run BusKill is using a simple udev config as described here:

 * https://www.buskill.in/buskill-laptop-kill-cord-dead-man-switch/

# Press

As seen on [PCMag](https://www.pcmag.com/news/372806/programmers-usb-cable-can-kill-laptop-if-machine-is-yanked), [Forbes](https://www.forbes.com/sites/daveywinder/2020/01/03/this-20-usb-cable-is-a-dead-mans-switch-for-your-linux-laptop/), [ZDNet](https://www.zdnet.com/article/new-usb-cable-kills-your-linux-laptop-if-stolen-in-a-public-place/), & [Tom's Hardware](https://www.tomshardware.com/news/the-buskill-usb-cable-secures-your-laptop-against-thieves).

# Contact

To contact us via email, please visit:

 * https://www.buskill.in/contact/

# License

The contents of this repo are dual-licensed. All code is GPLv3 and all other content is CC-BY-SA.

# For more Information

See https://tech.michaelaltfield.net/2020/01/02/buskill-laptop-kill-cord-dead-man-switch/
