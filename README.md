![](https://github.com/maltfield/cross-platform-python-gui/workflows/build/badge.svg)

# Cross Platform Python GUI

This repo is a fork-ready base for new your cross-platform, python-based GUI application.

It includes the CI pipeline to automatically build self-contained executables for Linux (AppImage), Windows (exe), and MacOS (dmg).

# How to use this repo

1. Fork this repo
2. Edit [src/main.py](/src/main.py) as needed
3. Add any required python modules to [requirements.txt](/requirements.txt)

When you push git commits to github on master, github will automatically spin up containers in the cloud and build your application's executables for all target platforms.

# TODO

1. Finish CI workflow for building MacOS .dmg apps

# License

The contents of this repo are dual-licensed. All code is GPLv3 and all other content is CC-BY-SA.
