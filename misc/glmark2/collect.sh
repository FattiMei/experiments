#!/bin/bash

GLMARK2_BENCHMARKS=$(compgen -c glmark2)

# DRM runs are only available from a virtual terminal
# I am storing the result in a variable to check only once
if [[ "$(tty)" == /dev/tty[0-9]* ]]; then
	IS_VIRTUAL_TERMINAL=true
else
	IS_VIRTUAL_TERMINAL=false
fi

for BENCHMARK in $GLMARK2_BENCHMARKS; do
	RESULTS_FILENAME="$BENCHMARK-results.txt"
	BENCHMARK_FULL_PATH=$(which $BENCHMARK)

	if [[ "$BENCHMARK" == *"drm" ]]; then
		if [ "$IS_VIRTUAL_TERMINAL" = true ]; then
			$BENCHMARK_FULL_PATH > "$RESULTS_FILENAME"
		else
			echo "$BENCHMARK needs a virtual terminal to be run"
		fi
	else
		if [[ -n "$DISPLAY" ]]; then
			$BENCHMARK_FULL_PATH > "$RESULTS_FILENAME"
		else
			sudo xinit $BENCHMARK_FULL_PATH -- :0 > "$RESULTS_FILENAME"
		fi
	fi
done
