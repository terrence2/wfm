#!/usr/bin/python3
"""
Clean in the directory specified, or the one currently linked as ./build.
"""

import os.path
import subprocess
import sys

import lib

def main():
    args, extra = lib.setup_build_api('Run |make clean|.')
    p = subprocess.Popen(['make', 'clean'] + extra, cwd=args.builddir)
    p.wait()
    return 0

if __name__ == '__main__':
    sys.exit(main())
