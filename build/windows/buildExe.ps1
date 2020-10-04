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
# Updated: 2020-10-04
# Version: 0.3
################################################################################

######################################
#### A Note about ' | Out-String' ####
######################################
# Strangely, when PowerShell calls any '.exe', it appears to have an implicit
# amp-off effect where that .exe is executed in the background and the next
# command is initiated without waiting. This creates tons of nondeterministic
# and undesired behaviour. The fix is a hack: just append ' | Out-String' to the
# end of an .exe call, and it will prevent it from running in the background,
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

# https://reproducible-builds.org/docs/source-date-epoch/
$env:SOURCE_DATE_EPOCH="$(git log -1 --pretty=%ct)"

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

$env:VERSION="$( git symbolic-ref HEAD | select -first 1 )"
$env:VERSION="$( $env:VERSION.Split( "/") | select -last 1 )"
if ( $env:VERSION -eq 'dev' ){
	$env:VERSION="$env:SOURCE_DATE_EPOCH"
}

$env:ARCHIVE_DIR="buskill-win-$env:VERSION-x86_64"
$env:ARCHIVE_SUBDIR="buskill-$env:VERSION-x86_64"

########
# INFO #
########

Write-Output "listing contents of C drive root"
Get-ChildItem -Path C:\ -Force | Out-String

Write-Output "listing contents of cwd"
Get-ChildItem -Force | Out-String

# TODO: delete these
# try to find the gpgv binary
Get-Command gpgv
Get-Command gpgv.exe
#Get-ChildItem -Filter "*msys-bz2-1.dll" -Recurse C:\ | Out-String

Write-Output 'INFO: Beginning execution'

###################
# INSTALL DEPENDS #
###################

# See https://docs.python.org/3.7/using/windows.html#installing-without-ui
Write-Output 'INFO: Installing python'
New-Item -Path C:\tmp -Type Directory | Out-String
New-Item -Path C:\tmp\python -Type Directory | Out-String
.\build/deps/python-3.7.8-amd64.exe /passive TargetDir=C:\tmp\python IncludePip=1 | Out-String

Write-Output 'INFO: Installing pip, setuptools, and virtualenv' | Out-String

C:\tmp\python\python.exe -m pip install --ignore-installed --upgrade --cache-dir .\build\deps\ --no-index --find-links .\build\deps\ .\build\deps\pip-20.1.1-py2.py3-none-any.whl | Out-String
C:\tmp\python\python.exe -m pip install --ignore-installed --upgrade --cache-dir .\build\deps\ --no-index --find-links .\build\deps\ .\build\deps\wheel-0.34.2-py2.py3-none-any.whl | Out-String
C:\tmp\python\python.exe -m pip install --ignore-installed --upgrade --cache-dir .\build\deps\ --no-index --find-links .\build\deps\ .\build\deps\setuptools-49.1.0-py3-none-any.whl | Out-String
C:\tmp\python\python.exe -m pip install --ignore-installed --upgrade --cache-dir .\build\deps\ --no-index --find-links .\build\deps\ .\build\deps\virtualenv-20.0.26-py2.py3-none-any.whl | Out-String

Write-Output 'INFO: Installing Python Depends'
New-Item -Path C:\tmp\kivy_venv -Type Directory | Out-String
C:\tmp\python\python.exe -m virtualenv C:\tmp\kivy_venv | Out-String
C:\tmp\kivy_venv\Scripts\activate.ps1 | Out-String

C:\tmp\kivy_venv\Scripts\python.exe -m pip install --ignore-installed --upgrade --cache-dir .\build\deps\ --no-index --find-links .\build\deps\ .\build\deps\pypiwin32-223-py3-none-any.whl | Out-String
C:\tmp\kivy_venv\Scripts\python.exe -m pip install --ignore-installed --upgrade --cache-dir .\build\deps\ --no-index --find-links .\build\deps\ .\build\deps\kivy_deps.sdl2-0.2.0-cp37-cp37m-win_amd64.whl | Out-String
C:\tmp\kivy_venv\Scripts\python.exe -m pip install --ignore-installed --upgrade --cache-dir .\build\deps\ --no-index --find-links .\build\deps\ .\build\deps\kivy_deps.glew-0.2.0-cp37-cp37m-win_amd64.whl | Out-String
C:\tmp\kivy_venv\Scripts\python.exe -m pip install --ignore-installed --upgrade --cache-dir .\build\deps\ --no-index --find-links .\build\deps\ .\build\deps\kivy_deps.angle-0.2.0-cp37-cp37m-win_amd64.whl | Out-String
C:\tmp\kivy_venv\Scripts\python.exe -m pip install --ignore-installed --upgrade --cache-dir .\build\deps\ --no-index --find-links .\build\deps\ .\build\deps\PyInstaller-3.6.tar.gz | Out-String

# install kivy and all other python dependencies with pip into our virtual env
C:\tmp\kivy_venv\Scripts\python.exe -m pip install --ignore-installed --upgrade --cache-dir .\build\deps\ --no-index --find-links .\build\deps\ .\build\deps\Kivy-1.11.1-cp37-cp37m-win_amd64.whl | Out-String

# INSTALL LATEST PIP PACKAGES
# (this can only be done for packages that are cryptographically signed
#  by the developer)

# python-gnupg
#  * https://bitbucket.org/vinay.sajip/python-gnupg/issues/137/pgp-key-accessibility
#  * https://github.com/BusKill/buskill-app/issues/6#issuecomment-682971392

# create temporary directory
$tmpDir = Join-Path $Env:Temp $(New-Guid)
echo "${tmpDir}"
New-Item -Path "${tmpDir}" -Type Directory | Out-String
if ( $LastExitCode -ne 0 ){
	echo "ERROR: Failed to create tmpDir" | Out-String
	exit 1 | Out-String
}
pushd "${tmpDir}"

# download the latest version of the python-gnupg module
C:\tmp\kivy_venv\Scripts\python.exe -m pip download python-gnupg | Out-String
$filename = Get-ChildItem -Name | Select-Object -First 1
echo $filename | Out-String

# get the URL to download the detached signature file
$signature_url = (curl -UseBasicParsing https://pypi.org/simple/python-gnupg/).Content.Split([Environment]::NewLine) | sls -Pattern "https://.*$filename#"
$signature_url = ($signature_url).matches | select -exp value | Out-String
$signature_url = ($signature_url).replace( '#', '.asc' ) | Out-String
echo $signature_url | Out-String
curl -OutFile "${filename}.asc" "${signature_url}" | Out-String
ls 

# prepare homedir and keyring for `gpgv`
mkdir gnupg | Out-String
#chmod 0700 gnupg
popd | Out-String
gpg --homedir "${tmpDir}\gnupg" --import "build\deps\python-gnupg.asc" | Out-String
ls "${tmpDir}\gnupg" | Out-String

# confirm that the signature is valid. `gpgv` would exit 2 if the signature
# isn't in our keyring (so we are effectively pinning it), it exits 1 if there's
# any BAD signatures, and exits 0 "if everything is fine"
gpgv --homedir "${tmpDir}\gnupg" --keyring "pubring.kbx" "${tmpDir}\${filename}.asc" "${tmpDir}\${filename}" | Out-String
echo "LastExitCode:" | Out-String
echo $LastExitCode | Out-String
if ( $LastExitCode -ne 0 ){
	echo "ERROR: Invalid PGP signature!" | Out-String
	exit 1 | Out-String
}

pushd "${tmpDir}" | Out-String
C:\tmp\kivy_venv\Scripts\python.exe -m pip install --ignore-installed --upgrade --cache-dir .\build\deps\ --no-index --find-links "." "${filename}" | Out-String
popd | Out-String
rm -Recurse -Force "${tmpDir}" | Out-String

# output information about this build so the code can use it later in logs
echo "# -*- mode: python ; coding: utf-8 -*-
BUSKILL_VERSION = {
 'VERSION': '$env:VERSION',
 'GITHUB_REF': '$env:GITHUB_REF',
 'GITHUB_SHA': '$env:GITHUB_SHA',
 'SOURCE_DATE_EPOCH': '$env:SOURCE_DATE_EPOCH',
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
             datas=
              [
               ( '..\\KEYS', '.' ),
               ( '..\\src\\images\\buskill-icon-150.png', '.' ),
               ('C:\\Program Files\\Git\\usr\\bin\\gpg.exe', '.'),
               ('C:\\msys64\\usr\\bin\\msys-bz2-1.dll', '.'),
               ('C:\\msys64\\usr\\bin\\msys-assuan-0.dll', '.'),
               ('C:\\msys64\\usr\\bin\\msys-gcrypt-20.dll', '.'),
               ('C:\\msys64\\usr\\bin\\msys-gpg-error-0.dll', '.'),
               ('C:\\msys64\\usr\\bin\\msys-2.0.dll', '.'),
               ('C:\\msys64\\usr\\bin\\msys-readline8.dll', '.'),
               ('C:\\msys64\\usr\\bin\\msys-z.dll', '.'),
               ('C:\\msys64\\usr\\bin\\msys-sqlite3-0.dll', '.'),
               ('C:\\msys64\\usr\\bin\\msys-iconv-2.dll', '.'),
               ('C:\\msys64\\usr\\bin\\msys-intl-8.dll', '.'),
               ('C:\\msys64\\usr\\bin\\msys-ncursesw6.dll', '.'),
              ],
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
          icon='..\\src\\images\\buskill-icon-150.ico',
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
C:\tmp\kivy_venv\Scripts\python.exe -m PyInstaller --noconfirm --onefile .\buskill.spec | Out-String

# attempt to execute it?
#.\dist\buskill\buskill.exe | Out-String

#####################
# PREPARE ARTIFACTS #
#####################

# return to the root of our build dir
cd .. | Out-String

New-Item -Path dist -Type Directory | Out-String
cp -r .\pyinstaller\dist\buskill "dist/${env:ARCHIVE_DIR}/${env:ARCHIVE_SUBDIR}" | Out-String

# add in docs/ dir
$docsDir = "dist\${env:ARCHIVE_DIR}\docs"
echo $docsDir
New-Item -Path "${docsDir}" -Type Directory | Out-String
cp "docs\README.md" "${docsDir}\" | Out-String
cp "docs\attribution.rst" "${docsDir}\" | Out-String
cp "LICENSE" "${docsDir}\" | Out-String
cp "CHANGELOG" "${docsDir}\" | Out-String
cp "KEYS" "${docsDir}\" | Out-String

Get-ChildItem -Path "dist" -Force | Out-String
cd dist

# create symlink (shortcut)
ls
cd ${env:ARCHIVE_DIR}
ls
cmd /C mklink buskill .\${env:ARCHIVE_SUBDIR}\buskill.exe
ls
cd ..
ls

Compress-Archive -DestinationPath "$env:ARCHIVE_DIR.zip" -Path "$env:ARCHIVE_DIR" | Out-String

#######################
# OUTPUT VERSION INFO #
#######################

Write-Output 'INFO: Dir contents'
Get-ChildItem -Path "pyinstaller" -Force | Out-String
Get-ChildItem -Path "pyinstaller\dist" -Force | Out-String
Get-ChildItem -Path "dist" -Force | Out-String

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
