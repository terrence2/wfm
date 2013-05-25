#!/usr/bin/python3
"""
Clone from ~/moz/trunk/<reponame> into ~/moz/branch/<foo>/mozilla

-b/--base to specify reponame
<arg+> to specify branchname to create
"""

import argparse
import os
import os.path
import subprocess
import sys

def main():
    # Process args.
    parser = argparse.ArgumentParser(description='Run make in a directory.')
    parser.add_argument('-b', '--base', metavar='BASE', default='mozilla-inbound', type=str,
                        help='Base of branch.')
    parser.add_argument('branches', metavar='BRANCH', type=str, nargs='+',
                        help='The branch(es) to create.')
    args, extra = parser.parse_known_args()

    # Expand the base path.
    basepath = '~/moz/trunk/{}'.format(args.base)
    basepathExpanded = os.path.realpath(os.path.expanduser(basepath))
    if not os.path.isdir(basepathExpanded):
        print("Base {} not found at {}\n  Expanded to {}".format(args.base,
            basepath, basepathExpanded))
        return 1

    # Clone to each branch.
    for branch in args.branches:
        branchpathBase = '~/moz/branch/{}'.format(branch)
        branchpathBase = os.path.realpath(os.path.expanduser(branchpathBase))
        if os.path.exists(branchpathBase):
            print("Branch directory {} already exists!\n  Expanded to {}".format(
                branch, branchpathBase))
            return 1
        os.mkdir(branchpathBase)
        branchpath = os.path.join(branchpathBase, 'mozilla')
        subprocess.call(['hg', 'clone', basepathExpanded, branchpath])

    return 0

if __name__ == '__main__':
    sys.exit(main())
