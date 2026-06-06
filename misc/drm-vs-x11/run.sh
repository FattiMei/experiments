#!/bin/bash

# This script has been designed to include mutually exclusive use cases:
#   1. DRM and xinit experiments need to be run in a virtual terminal
#   2. X11 experiment needs an active X11 display
#
# I use if statement to check if the conditions for the experiments are satisfied

GLMARK2_DRM_EXE=glmark2-es2-drm
GLMARK2_X11_EXE=glmark2-es2

GLMARK2_DRM_RESULTS="glmark2_drm_results.txt"
GLMARK2_XINIT_RESULTS="glmark2_xinit_results.txt"
GLMARK2_X11_RESULTS="glmark2_x11_results.txt"

if [[ "$(tty)" == /dev/tty[0-9]* ]]; then
	echo "Launching DRM experiment"
	$GLMARK2_DRM_EXE > "$GLMARK2_DRM_RESULTS"

	# `xinit` requires the full program path
	GLMARK2_X11_FULL_PATH=$(which $GLMARK2_X11_EXE)

	echo "Launching xinit experiment"
	sudo xinit $GLMARK2_X11_FULL_PATH -- :0 > "$GLMARK2_XINIT_RESULTS"
else
	echo "drm and xinit experiments need to run in a VT, skipping them..."
	echo "try to run sudo openvt -w $0..."
fi

if [[ -n "$DISPLAY" ]]; then
	echo "Launching X11 experiment"
	$GLMARK2_X11_EXE > "$GLMARK2_X11_RESULTS"
else
	echo "There isn't an active X11 session, skipping X11 experiment..."
fi
