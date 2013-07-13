#!/usr/bin/env python3
# This program configures SpiderMonkey on a remote machine with whatever
# configuration is specified. It does this by rsyncing '.' with the remote
# host, ssh -e 'conf ...', then rsyncing back. Build proceeds in a similar
# manner. Even though the configuration parameters are the same locally or
# remotely, it is important to configure a build directory remotely before an
# rbuild so that the right system headers/libs get pulled in and checked for
# compatibility.

import argparse
import os
import os.path
import subprocess
import sys


def pick_remotedir(username):
    """
    Return a stable name based on our host and current branch.
    """
    # Lookup up until we find 'mozilla', then one above that.
    pwd = os.getcwd()
    while os.path.basename(pwd) != 'mozilla':
        pwd = os.path.dirname(pwd)
    pwd = os.path.dirname(pwd)
    branch = os.path.basename(pwd)

    return (os.path.sep +
            os.path.join('home', username, 'moz', branch, 'js', 'src') +
            os.path.sep)


def main():
    parser = argparse.ArgumentParser(description="Configure SpiderMonkey for" +
                                     " a remote build to run locally.")
    parser.add_argument('--user', '-u', metavar='USER', type=str,
                        default=os.environ['USER'],
                        help="Username to log into remote machine with.")
    parser.add_argument('host', metavar='HOST', type=str, nargs=1,
                        help="The host to configure on.")
    parser.add_argument('builddir', metavar='CONTEXT', type=str, nargs='?',
                        help="The configuration to use.")
    args, extra = parser.parse_known_args()

    targetdir = pick_remotedir(args.user)
    userAtHost = args.user + '@' + args.host
    userHostDir = userAtHost + ':' + targetdir

    # ssh user@host mkdir -p targetdir
    subprocess.check_call('ssh', userAtHost, 'mkdir', '-p', targetdir)

    # rsync -avx -e ssh ./ user@host:targetdir
    subprocess.check_call('rsync', '-avx', '-e', 'ssh', './', userHostDir)

    # ssh user@host

if __name__ == '__main__':
    sys.exit(main())
