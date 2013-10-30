#!/usr/bin/python3
"""
Build in the directory specified, or the one currently linked as ./build.

-j# is specified by int(arg0)

TODO:
    Attempt to parallelize linking as well.
"""

import argparse
import os.path
import subprocess
import sys

import lib

def main():
    # Process args.
    parser = argparse.ArgumentParser(description='Run make in a directory.')
    parser.add_argument('builddir', metavar='CONTEXT', default='ctx', type=str, nargs='?',
                        help='The directory to build in.')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show all build output.')
    parser.add_argument('--jobs', '-j', metavar='count', default=0, type=int,
                        help='Number of parallel builds to run.')
    parser.add_argument('--parallel', '-p', action='store_true',
                        help='Try to link jsapi-tests in parallel with shell.')
    args, extra = parser.parse_known_args()

    # Check for build-dir.
    if not os.path.isdir(args.builddir):
        raise Exception("No directory at builddir: {}".format(args.builddir))

    # Get the process count.
    extra += ['-j' + str(lib.get_jobcount(args.jobs))]

    # Default to silent build.
    if not args.verbose:
        extra += ['-s']

    # Try parallel build if requested
    if args.parallel:
        p = subprocess.Popen(['make'] + extra + ['libjs_static.a'], cwd=args.builddir)
        p.wait()

        p0 = subprocess.Popen(['make', '-C', 'jsapi-tests'] + extra, cwd=args.builddir)
        p1 = subprocess.Popen(['make', '-C', 'shell'] + extra, cwd=args.builddir)
        p0.wait()
        p1.wait()
    else:
        p = subprocess.Popen(['make'] + extra, cwd=args.builddir)
        p.wait()

    return 0

if __name__ == '__main__':
    sys.exit(main())
