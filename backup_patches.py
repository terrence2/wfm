#!/usr/bin/env python3
import os
import os.path
import shutil

def pull(branchdir, targetdir):
    if not os.path.isdir(targetdir):
        os.makedirs(targetdir)

    trees = os.listdir(branchdir)
    for tree in trees:
        patchdir = os.path.join(branchdir, tree, '.hg/patches/')
        backupdir = os.path.join(targetdir, tree)
        if os.path.exists(backupdir):
            print("Target directory {} already exists.".format(backupdir))
            return

        shutil.copytree(patchdir, backupdir)


pull("/home/terrence/moz/branch", "/home/terrence/moz/backup_patches/")

