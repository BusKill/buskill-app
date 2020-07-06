$ErrorActionPreference = 'continue'
Set-PSDebug -Trace 1
################################################################################
# File:    windows/buildExe.ps1
# Purpose: Builds a windows executable for a simple Hello World GUI app using
#          using kivy. See also:
#
#          * https://kivy.org/doc/stable/installation/installation-windows.html
#          * https://kivy.org/doc/stable/guide/packaging-windows.html
#          * https://github.com/kivy/kivy/issues/6906
#
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-05-31
# Updated: 2020-05-31
# Version: 0.1
################################################################################

######################################
#### A Note about ' | Out-String' ####
######################################
# Straingely, when PowerShell calls any '.exe', it appears to have an implicit
# amp-off effect where that .exe is executed in the background and the next
# command is initiated without waiting. This creates tons of nondeterministic
# and undesired behaviour. The fix is a hack: just append ' | Out-String' to the
# end of an .exe call, and it will prevent it from running in the backgound,
# delaying the subsequent line from running until the current line finishes
######################################

############
# SETTINGS #
############

$env:APP_NAME="buskill"

# make PyInstaller produce reproducible builds. This will only affect the hash
# randomization at build time. When the frozen app built by PyInstaller is
# executed, hash randomization will be enabled (per defaults)
# * https://pyinstaller.readthedocs.io/en/stable/advanced-topics.html#creating-a-reproducible-build
# * https://docs.python.org/3/using/cmdline.html#cmdoption-r
$env:PYTHONHASHSEED=0

#################
# FIX CONSTANTS #
#################

# fill-in some constants if this script is not being run on GitHub
if ( ! $env:GITHUB_REF ){ 
	# TODO convert this bash to powershelll
	#GITHUB_REF=`git show-ref | head -n1 | awk '{print $2}'`
	$env:GITHUB_REF="???"
}
if ( ! $env:GITHUB_SHA ){ 
	# TODO convert this bash to powershelll
	#GITHUB_SHA=`git show-ref | head -n1 | awk '{print $1}'`
	$env:GITHUB_SHA="???"
}

########
# INFO #
########

Write-Output "listing contents of C drive root"
Get-ChildItem -Path C:\ -Force | Out-String

Write-Output "listing contents of cwd"
Get-ChildItem -Force | Out-String

Write-Output 'INFO: Beginning execution'

###################
# INSTALL DEPENDS #
###################

# it looks like we can't use the smaller embeddable zip file as it lacks pip
#curl -OutFile python3.7.zip https://www.python.org/ftp/python/3.7.7/python-3.7.7-embed-amd64.zip
#Expand-Archive .\python3.7.zip

# See https://docs.python.org/3.7/using/windows.html#installing-without-ui
Write-Output 'INFO: Downloading python3.7'
curl -OutFile python3.7.exe https://www.python.org/ftp/python/3.7.7/python-3.7.7-amd64.exe | Out-String

Write-Output 'INFO: Installing python'
New-Item -Path C:\tmp -Type Directory | Out-String
New-Item -Path C:\tmp\python -Type Directory | Out-String
.\python3.7.exe /passive TargetDir=C:\tmp\python IncludePip=1 | Out-String

Write-Output 'INFO: Installing pip, setuptools, and virtualenv' | Out-String
C:\tmp\python\python.exe -m pip install --upgrade --user pip wheel setuptools virtualenv | Out-String

Write-Output 'INFO: Installing Python Depends'
New-Item -Path C:\tmp\kivy_venv -Type Directory | Out-String
C:\tmp\python\python.exe -m virtualenv C:\tmp\kivy_venv | Out-String
C:\tmp\kivy_venv\Scripts\activate.ps1 | Out-String
C:\tmp\kivy_venv\Scripts\python.exe -m pip install --upgrade pypiwin32 kivy_deps.sdl2 kivy_deps.glew kivy_deps.angle | Out-String

# install kivy and all other python dependencies with pip into our virtual env
C:\tmp\kivy_venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt | Out-String

# output information about this build so the code can use it later in logs
echo "# -*- mode: python ; coding: utf-8 -*-
BUSKILL_VERSION = {
 'GITHUB_REF': '$env:GITHUB_REF',
 'GITHUB_SHA': '$env:GITHUB_SHA',
}
" | tee .\src\buskill_version.py
(Get-Content .\src\buskill_version.py) -replace "`0", "" | Set-Content .\src\buskill_version.py

##################################
# PREPARE BUILD WITH PYINSTALLER #
##################################

Write-Output 'INFO: Prepare our exe'
C:\tmp\kivy_venv\Scripts\python.exe -m pip install --upgrade pyinstaller | Out-String
New-Item -Path pyinstaller -Type Directory | Out-String
cd pyinstaller | Out-String

echo "# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import angle, glew, sdl2

block_cipher = None


a = Analysis(['..\\src\\main.py'],
             pathex=['.\\'],
             binaries=[],
             datas=[],
             hiddenimports=['pkg_resources.py2_warn', 'libusb1'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='buskill',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe, Tree('..\\src\\'),
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (glew.dep_bins + angle.dep_bins + sdl2.dep_bins)],
               strip=False,
               upx=True,
               upx_exclude=[],
               name='buskill')
" | tee buskill.spec

# PyInstaller in windows chokes on null bytes added to .spec files; remove them
# to prevent "ValueError: source code string cannot contain null bytes"
(Get-Content .\buskill.spec) -replace "`0", "" | Set-Content .\buskill.spec

#############
# BUILD EXE #
#############

# VMs need to use angle, and apparently PyInstaller doesn't see the os.environ
# call in the code itself, so we have to set it in PowerShell directly. This
# fixes the error:
#   "[CRITICAL] [App         ] Unable to get any Image provider, abort.
$env:KIVY_GL_BACKEND="angle_sdl2"

# build it from the spec file
C:\tmp\kivy_venv\Scripts\python.exe -m PyInstaller --noconfirm .\buskill.spec | Out-String

# attempt to execute it?
#.\dist\buskill\buskill.exe | Out-String

#####################
# PREPARE ARTIFACTS #
#####################

# return to the root of our build dir
cd .. | Out-String

New-Item -Path dist -Type Directory | Out-String
cp -r .\pyinstaller\dist\buskill dist/buskill-x86_64 | Out-String

#######################
# OUTPUT VERSION INFO #
#######################

Write-Output 'INFO: Python versions info'

# before exiting, output the versions of software installed
C:\tmp\kivy_venv\Scripts\python.exe --version | Out-String
C:\tmp\kivy_venv\Scripts\python.exe -m pip list | Out-String

# print all environment variables
Get-ChildItem env:

##################
# CLEANUP & EXIT #
##################

# TODO?
