#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
import pathlib
import os

from utility import pathutils
from providers.provider import Provider

class PythonSync(Provider):
    __slots__ = (r'__remotes',)

    def __init__(self, path, out = None):
        self.__remotes = {}
        super().__init__(path, out)

    def isPullSupport(self):
        return True

    def isPushSupport(self):
        return True

    def isCommitSupport(self):
        return False

    def isCloneSupport(self):
        return True

    def isValid(self):
        return not pathutils.isUrl(self.path)

    def addRemotes(self, remoteName, remotes):
        if not remoteName in self.__remotes:
            self.__remotes[remoteName] = []
        for remote in remotes:
            if isinstance(remote, pathlib.Path) and remote.exists() and remote.is_dir():
                self.__remotes[remoteName].append(remote)

    def commit(self, message, addAll): # pylint: disable=unused-argument
        return -1

    def pull(self, remote, opts):
        if not remote in self.__remotes:
            return -1
        for path in self.__remotes[remote]:
            self.__comparePath(path, self.path, remote, opts)
        return 0

    def push(self, remote, opts):
        if not remote in self.__remotes:
            return -1
        for path in self.__remotes[remote]:
            self.__comparePath(self.path, path, remote, opts)
        return 0

    def clone(self, remote, opts):
        if not remote in self.__remotes:
            return -1
        if not self.path.exists() or not self.path.is_dir():
            self.path.mkdir(parents=True)
        for path in self.__remotes[remote]:
            self.__copyTree(path, self.path, opts)
            return 0
        return -1

    def __copyWithProgress(self, src, dst, *args, follow_symlinks=True):
        self.out(str(src) + r' -> ' + str(dst), False)
        return shutil.copy2(src, dst, *args, follow_symlinks=follow_symlinks)

    def __compare2file(self, file1, file2):
        with file1.open(r'rb') as f1:
            with file2.open(r'rb') as f2:
                f1It = iter(f1.read, 5120)
                f2It = iter(f2.read, 5120)

                while True:
                    chunck1 = next(f1It, None)
                    chunck2 = next(f2It, None)
                    if not chunck1 or not chunck2:
                        return chunck1 == chunck2
                    if chunck1 != chunck2:
                        break
        return False

    def __comparePath(self, source_path, target_path, remoteName, opts):
        if source_path.exists() and source_path.is_dir():
            self.__compareFolder(source_path, target_path, remoteName, opts)

    def __copyTree(self, source_item, target_item, opts):
        shutil.copytree(source_item, target_item, symlinks=(r'symlinks' in opts), \
                        copy_function=lambda src, dst, *args, fsymlinks=True: \
                        self.__copyWithProgress(src, dst, *args, follow_symlinks=fsymlinks))

    def __compareFolder(self, source, target, remoteName, opts):
        for source_item in source.iterdir():
            target_item = target / source_item.name
            if target_item.exists():
                if source_item.is_dir():
                    self.__compareFolder(source_item, target_item, remoteName, opts)
                else:
                    self.__checkFiles(source_item, target_item, remoteName, opts)
            else:
                if source_item.is_dir():
                    self.__copyTree(source_item, target_item, opts)
                else:
                    self.__copyWithProgress(source_item, target_item,
                                            follow_symlinks=r'symlinks' in opts)
        return True

    def __checkFiles(self, source, target, remoteName, opts):
        sourceInfo = source.lstat()
        targetInfo = target.lstat()
        cmpFiles = r'fullcmp' in opts
        fsymlinks = r'symlinks' in opts

        if sourceInfo.st_mtime == targetInfo.st_mtime:
            if not r'noconflicts' in opts:
                if (sourceInfo.st_size != targetInfo.st_size) or \
                   (cmpFiles and not self.__compare2file(source, target)):
                    self.out(r'Conflict: ' + str(source) + r' -> ' + str(target) +
                             r' (equal modification time files with different content)',
                             False)
                    self.__copyWithProgress(source,
                                            target.with_suffix(r'.conflict.' + remoteName),
                                            follow_symlinks=fsymlinks)
            return

        if sourceInfo.st_mtime < targetInfo.st_mtime:
            return

        if not cmpFiles or not self.__compare2file(source, target):
            self.__copyWithProgress(source, target, follow_symlinks=fsymlinks)
        else:
            os.utime(target, (sourceInfo.st_mtime, sourceInfo.st_mtime))
