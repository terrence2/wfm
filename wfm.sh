#!/bin/bash
# The windows mozilla-build only ships python2. This means that there is no
# python3 in path. Instead of fiddling with paths and polluting the build
# environment, we launch with this shell script.
/c/Python34/python ~/moz/wfm/wfm.py "$@"

