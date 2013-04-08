#!/usr/bin/python3
"""
Build in the directory specified, or the one currently linked as ./build.

-j# is specified by int(arg0)
Will attempt to parallelize linking as well.
"""

import argparse
import contextlib
import os
import os.path
import subprocess
import sys

@contextlib.contextmanager
def cd(dirname):
    current = os.getcwd()
    os.chdir(dirname)
    try:
        yield
    finally:
        os.chdir(current)

def main():
    # Process args.
    parser = argparse.ArgumentParser(description='Run make in a directory.')
    parser.add_argument('builddir', metavar='context', default='ctx', type=str, nargs='?', help='The directory to build in.')
    parser.add_argument('--jobs', '-j', metavar='count', default=0, type=int, help='Number of parallel builds to run.')
    args, extra = parser.parse_known_args()

    # Get the process count.
    cnt = args.jobs
    if not cnt:
        cmdname = sys.argv[0].strip('./\\')
        if cmdname.isdigit():
            cnt = int(cmdname)
        else:
            cnt = 1
    extra += ['-j' + str(cnt)]

    if not os.path.isdir(args.builddir):
        print("No directory at builddir: {}".format(args.builddir))
        return 1

    with cd(args.builddir):
        p = subprocess.Popen(['make'] + extra)
        p.communicate(4096)

    return 0

if __name__ == '__main__':
    sys.exit(main())
