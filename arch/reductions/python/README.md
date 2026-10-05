This folder contains a python implementation that almost matches the C++ one.

The results obtained from this JIT pipeline are hard to explain as the python interpreter adds overheads.
Some of those overheads could be removed with careful data analysis, for example by modeling the benchmark latency as an affine function of the input size.
Seeing a night and day difference between the two implementations, I decided to keep the python version only as a *memento* about the value of lean runtimes and predictable behaviours.

Nevertheless this version has precious features:
  * data acquisition parameters with command line arguments
  * possibility of examining the LLVM IR and controlling the vectorization pass

It's not impossible to integrate some IR inspection into C++ workflows, but it's not a priority, now that we know the general parallelization strategy.
I still can't pinpoint the exact overheads, which could be from the python interpreter or the JIT module. Further profiling results from the python runtime have to be checked carefully.

Mei Matteo - 05/10/2026

