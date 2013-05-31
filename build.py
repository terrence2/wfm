#!/usr/bin/python3
"""
Build in the directory specified, or the one currently linked as ./build.

-j# is specified by int(arg0)

TODO:
    Attempt to parallelize linking as well.
"""

import os.path
import subprocess
import sys

import lib

def main():
    # Process args.
    args, extra = lib.setup_build_api('Run make in a directory.')

    # Get the process count.
    extra += ['-j' + str(args.jobs)]

    # Default to silent build.
    if not args.verbose:
        extra += ['-s']

    p = subprocess.Popen(['make'] + extra, cwd=args.builddir)
    p.wait()

    return 0

if __name__ == '__main__':
    sys.exit(main())
