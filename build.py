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

from multiprocessing import cpu_count

def get_jobcount(specified):
    if specified > 0:
        return specified

    cmdname = os.path.basename(sys.argv[0]).strip('./\\')
    try:
        return int(cmdname)
    except ValueError:
        pass

    return cpu_count()


def main():
    # Process args.
    parser = argparse.ArgumentParser(description='Run make in a directory.')
    parser.add_argument('builddir', metavar='CONTEXT', default='ctx', type=str, nargs='?',
                        help='The directory to build in.')
    parser.add_argument('--jobs', '-j', metavar='count', default=0, type=int,
                        help='Number of parallel builds to run.')
    parser.add_argument('--verbose', '-v', metavar='verbose', default=False, type=bool,
                        help='Show all build output.')
    args, extra = parser.parse_known_args()

    if not os.path.isdir(args.builddir):
        print("No directory at builddir: {}".format(args.builddir))
        return 1

    # Get the process count.
    extra += ['-j' + str(get_jobcount(args.jobs))]

    # Default to silent build.
    if not args.verbose:
        extra += ['-s']

    p = subprocess.Popen(['make'] + extra, cwd=args.builddir)
    p.wait()

    return 0

if __name__ == '__main__':
    sys.exit(main())
