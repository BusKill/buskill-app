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

Write-Output "listing contents of C drive root"
Get-ChildItem -Path C:\ -Force | Out-String

Write-Output "listing contents of cwd"
Get-ChildItem -Force | Out-String

Write-Output 'INFO: Beginning execution'

Write-Output "INFO: Inspect gitlab's python version"
Get-ChildItem -Path C:\Users\gitlab_runner -Force | Out-String
Get-ChildItem -Path C:\Users\gitlab_runner\AppData -Force | Out-String
Get-ChildItem -Path C:\Users\gitlab_runner\AppData\Roaming -Force | Out-String
Get-ChildItem -Path C:\Users\gitlab_runner\AppData\Roaming\Python -Force | Out-String
Get-ChildItem -Path C:\Users\gitlab_runner\AppData\Roaming\Python\Python37 -Force | Out-String
Get-ChildItem -Path C:\Users\gitlab_runner\AppData\Roaming\Python\Python37\Scripts -Force | Out-String

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
C:\tmp\kivy_venv\Scripts\python.exe -m pip install --upgrade docutils pygments pypiwin32 kivy_deps.sdl2 kivy_deps.glew kivy_deps.angle | Out-String

# install kivy and all other python dependencies with pip into our virtual env
C:\tmp\kivy_venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt | Out-String

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
             hiddenimports=['pkg_resources.py2_warn'],
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
          name='helloWorld',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (glew.dep_bins + angle.dep_bins + sdl2.dep_bins)],
               strip=False,
               upx=True,
               upx_exclude=[],
               name='helloWorld')
" | tee helloWorld.spec

# PyInstaller in windows chokes on null bytes added to .spec files; remove them
# to prevent "ValueError: source code string cannot contain null bytes"
(Get-Content .\helloWorld.spec) -replace "`0", "" | Set-Content .\helloWorld.spec

#############
# BUILD EXE #
#############

# VMs need to use angle, and apparently PyInstaller doesn't see the os.environ
# call in the code itself, so we have to set it in PowerShell directly. This
# fixes the error:
#   "[CRITICAL] [App         ] Unable to get any Image provider, abort.
$env:KIVY_GL_BACKEND="angle_sdl2"

# build it from the spec file
C:\tmp\kivy_venv\Scripts\python.exe -m PyInstaller --noconfirm .\helloWorld.spec | Out-String

# attempt to execute it?
.\dist\helloWorld\helloWorld.exe | Out-String

#####################
# PREPARE ARTIFACTS #
#####################

# return to the root of our build dir
cd .. | Out-String

New-Item -Path dist -Type Directory | Out-String
cp -r .\pyinstaller\dist\helloWorld dist/helloWorld-x86_64 | Out-String

#######################
# OUTPUT VERSION INFO #
#######################

Write-Output 'INFO: Python versions info'

# before exiting, output the versions of software installed
C:\tmp\kivy_venv\Scripts\python.exe --version | Out-String
C:\tmp\kivy_venv\Scripts\python.exe -m pip list | Out-String

##################
# CLEANUP & EXIT #
##################

# TODO?
