[![pipeline status](https://gitlab.com/maltfield/cross-platform-python-gui/badges/master/pipeline.svg)](https://gitlab.com/maltfield/cross-platform-python-gui/-/commits/master)

# Cross Platform Python GUI

This repo is a fork-ready base for new your cross-platform, python-based GUI application.

It includes the CI pipeline to automatically build self-contained executables for Linux (AppImage), Windows (exe), and MacOS (dmg).

# How to use this repo

1. Fork this repo
2. Edit [src/main.py](/src/main.py) as needed
3. Add any required python modules to [requirements.txt](/requirements.txt)
4. Go to Settings -> CI/CD and make sure that you have defined a a "General pipeline." The default settings should be fine.

When you push the above changes to master, gitlab will automatically spin up containers in GCP and build your application's executables for all target platforms.

# TODO

1. Add Windows CI job for building a Windows .exe
2. Figure out how to build a Mac release on gitlab shared runners in GCP (vagrant with libvirt?)

# License

The contents of this repo are dual-licensed. All code is GPLv3 and all other content is CC-BY-SA.
