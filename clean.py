#!/usr/bin/python3
"""
Clean in the directory specified, or the one currently linked as ./build.
"""

import os.path
import subprocess
import sys

import lib

def main():
    parser = lib.setup_build_api('Run |make clean|.')
    args, extra = parser.parse_known_args()
    p = subprocess.Popen(['make'] + extra, cwd=args.builddir)
    p.wait()
    return 0

if __name__ == '__main__':
    sys.exit(main())
