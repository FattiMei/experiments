#!/bin/sh

CACHE_DIR=/home/pi/.manview
OUTPUT=$CACHE_DIR/$1.pdf

set -e

mkdir -p $CACHE_DIR

if [ ! -f "$OUTPUT" ]; then
	echo "$OUTPUT doesn't exists, creating one"
	man -Tpdf $1 > $OUTPUT
fi

# don't open in background, this script should be called with dmenu
zathura $OUTPUT

