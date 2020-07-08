This dir holds all the files needed to build this app on all platforms. We store these files in the repo instead of downloading them at build-time because the tools used to download them do not provide secure authentication and integrity checks.

For more info, see:

 * https://github.com/BusKill/buskill-app/issues/2

There's a `SHA256SUMS` file in this directory that contains the sha256 hashes of the files in this directory.

You should also be able to use the `download.sh` script in this directory to re-download the assets.
