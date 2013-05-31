import argparse
import multiprocessing
import os.path
import sys

def get_jobcount(specified):
    if specified > 0:
        return specified

    cmdname = os.path.basename(sys.argv[0]).strip('./\\')
    try:
        return int(cmdname)
    except ValueError:
        pass

    return multiprocessing.cpu_count()

def setup_build_api(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('builddir', metavar='CONTEXT', default='ctx', type=str, nargs='?',
                        help='The directory to build in.')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show all build output.')
    parser.add_argument('--jobs', '-j', metavar='count', default=0, type=int,
                        help='Number of parallel builds to run.')
    args, extra = parser.parse_known_args()

    if not os.path.isdir(args.builddir):
        raise Exception("No directory at builddir: {}".format(args.builddir))

    args.jobs = get_jobcount(args.jobs)

    return args, extra
