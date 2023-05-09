#!/usr/bin/env python
# -*- coding: utf-8 -*-

from providers.provider import Provider
import utility.pathutils
import shutil
import pathlib
import os

class PythonSync(Provider):
    __slots__ = [r'__remotes']

    def __init__(self, path, out = None):
        self.__remotes = dict()
        super(PythonSync, self).__init__(path, out)
    
    def isPullSupport(self):
        return True
    
    def isPushSupport(self):
        return True
    
    def isCloneSupport(self):
        return False
    
    def isValid(self):
        return not(utility.pathutils.isUrl(self.path))
    
    def addRemotes(self, remoteName, remotes):
        if not(remoteName in self.__remotes):
            self.__remotes[remoteName] = []
        for remote in remotes:
            if not(utility.pathutils.isUrl(remote)):
                self.__remotes[remoteName].append(remote)
    
    def commit(self, message, addAll):
        return -1

    def pull(self, remote, opts):
        if not(remote in self.__remotes):
           return -1
        for path in self.__remotes[remote]:
            self.__comparePath(pathlib.Path(path), pathlib.Path(self.path), remote, opts)
        return 0
    
    def push(self, remote, opts):
        if not(remote in self.__remotes):
           return -1
        for path in self.__remotes[remote]:
            self.__comparePath(pathlib.Path(self.path), pathlib.Path(path), remote, opts)
        return 0
    
    def clone(self, remote, opts):
        if not(remote in self.__remotes):
           return -1
        for path in self.__remotes[remote]:
            source_path = pathlib.Path(path)
            if source_path.exists() and source_path.is_dir():
                self.__copyTree(source_path, pathlib.Path(self.path), opts)
                return 0
        return -1
    
    def __copyWithProgress(self, src, dst, *args, follow_symlinks=True):
        self.out(src + r' -> ' + dst, False)
        return shutil.copy2(src, dst, *args, follow_symlinks=follow_symlinks)

    def __compare2file(self, file1, file2):
        with file1.open(r'rb') as f1:
            with file2.open(r'rb') as f2:
                f1It = iter(lambda : f1.read(5120), r'')
                f2It = iter(lambda : f2.read(5120), r'')

                while True:
                    chunck1 = next(f1It, None)
                    chunck2 = next(f2It, None)
                    if (chunck1 == None) or (chunck2 == None):
                        return chunck1 == chunck2
                    if chunck1 != chunck2:
                        return False
        return False
    
    def __comparePath(self, source_path, target_path, remoteName, opts):
        if source_path.exists() and source_path.is_dir():
            self.__compareFolder(source_path, target_path, remoteName, opts)
    
    def __copyTree(self, source_item, target_item, opts):
        shutil.copytree(source_item, target_item, symlinks=(r'symlinks' in opts), \
                        copy_function=lambda src, dst, *args, follow_symlinks=True: \
                            self.__copyWithProgress(src, dst, *args, follow_symlinks=follow_symlinks))

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
                    self.__copyWithProgress(source_item, target_item, follow_symlinks=(r'symlinks' in opts))
        return True
    
    def __checkFiles(self, source, target, remoteName, opts):
        sourceInfo = source.lstat()
        targetInfo = target.lstat()
        cmpFiles = (r'fullcmp' in opts)

        if sourceInfo.st_mtime == targetInfo.st_mtime:
            if not(r'noconflicts' in opts):
                if (sourceInfo.st_size != targetInfo.st_size) or \
                   (cmpFiles and not(self.__compare2file(source, target))):
                    self.out(r'Conflict: ' + source + r' -> ' + target + r' (equal modification time files with different content)', False)
                    self.__copyWithProgress(source, target.with_suffix(r'.conflict.' + remoteName), follow_symlinks=(r'symlinks' in opts))
            return

        if sourceInfo.st_mtime < targetInfo.st_mtime:
            return

        if not(cmpFiles) or not(self.__compare2file(source, target)):
            self.__copyWithProgress(source, target, follow_symlinks=(r'symlinks' in opts))
        else:
            os.utime(target, (sourceInfo.st_mtime, sourceInfo.st_mtime))