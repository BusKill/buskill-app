#!/usr/bin/bash
################################################################################
# File:    optimize_images.sh
# Version: 0.1
# Purpose: Does lossless compression on all images in this repo to reduce size
# Authors: Francois Marier <https://fmarier.org>
# Co-Auth: Michael Altfield <michael@michaelaltfield.net>
# Created: 2024-03-16
# Updated: 2024-03-16
################################################################################

################################################################################
#                                  SETTINGS                                    #
################################################################################

################################################################################
#                                  FUNCTIONS                                   #
################################################################################

################################################################################
#                                  MAIN BODY                                   #
################################################################################

#################
# SANITY CHECKS #
#################

# this script isn't robust enough
if [ ! -e "`pwd`/build/$(basename $0)" ]; then
	echo "ERROR: This script should only be executed from the root of the github dir."
	exit 1
fi

###################
# INSTALL DEPENDS #
###################

yes | sudo DEBIAN_FRONTEND=noninteractive apt-get -yqq install gifsicle jpegoptim zopfli

##################
# CHECK SETTINGS #
##################

# na

####################
# HANDLE ARGUMENTS #
####################

# na

#####################
# DECLARE VARIABLES #
#####################

# na

###################
# Optimize Images #
###################

# PNGs
files=$(find . -iname '*.png')
for png_filename in $files; do
	echo $png_filename
	intermediate_filename="${png_filename}.zopfli"

	zopflipng -m --filters=01234mepb --lossy_transparent "$png_filename" "$intermediate_filename" > /dev/null

	input_size=$(stat --format=%s "$png_filename")
	output_size=$(stat --format=%s "$intermediate_filename")

	if test "$output_size" -lt "$input_size" ; then
    	mv "$intermediate_filename" "$png_filename"
		echo -e "\tINFO: optimized"
	else
		rm -f "$intermediate_filename"
		echo -e "\tINFO: skipped"
	fi
done

# GIFs
files=$(find . -iname '*.gif')
for filename in $files; do
	echo $filename
	gifsicle -O2 -b $filename
done
	
# JP(E)Gs
files=$(find . -iname '*.jpg')
files=${files}${IFS}$(find . -iname '*.jpeg')
for filename in $files; do
	echo $filename
	jpegoptim -p --strip-all $filename
done
