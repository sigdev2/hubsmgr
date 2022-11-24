#!/usr/bin/env python
# -*- coding: utf-8 -*-

from providers.provider import Provider
import shutil
import pathlib

class PythonSync(Provider):
    def __init__(self, hub, name, url, root, out = None):
        super(PythonSync, self).__init__(hub, name, url, root, out)
    
    def updateRemotes(self):
        return 0

    def commit(self, message, addAll):
        return 0

    def pull(self):
        self.__comparePath(pathlib.Path(self.url), self.path())
        return 0
    
    def push(self):
        self.__comparePath(self.path(), pathlib.Path(self.url))
        return 0
    
    def clone(self):
        source_path = pathlib.Path(self.url)
        if source_path.exists() and source_path.is_dir():
            self.__copyTree(source_path, self.path())
            return 0
        return 1
    
    def __copyWithProgress(self, src, dst, *args, follow_symlinks=True):
        self.out(src + r' -> ' + dst, False)
        return shutil.copy2(src, dst, *args, follow_symlinks=follow_symlinks)

    def __compare2file(self, file1, file2):
        with file1.open('rb') as f1:
            with file2.open('rb') as f2:
                f1It = iter(lambda : f1.read(5120), r'')
                f2It = iter(lambda : f2.read(5120), r'')

                while True:
                    chunck1 = next(f1It, None)
                    chunck2 = next(f2It, None)
                    if (chunck1 == None) or (chunck2 == None):
                        return chunck1 == chunck2
                    if chunck1 != chunck2:
                        return False
                return True
    
    def __comparePath(self, source_path, target_path):
        if source_path.exists() and source_path.is_dir():
            self.__compareFolder(source_path, target_path)
    
    def __copyTree(self, source_item, target_item):
        shutil.copytree(source_item, target_item, symlinks=(r'symlinks' in self.opts), \
                        copy_function=lambda src, dst, *args, follow_symlinks=True: \
                            self.__copyWithProgress(src, dst, *args, follow_symlinks=follow_symlinks))

    def __compareFolder(self, source, target):
        for source_item in source.iterdir():
            target_item = target / source_item.name
            if target_item.exists():
                if source_item.is_dir():
                    self.__compareFolder(source_item, target_item)
                else:
                    self.__checkFiles(source_item, target_item)
            else:
                if source_item.is_dir():
                    self.__copyTree(source_item, target_item)
                else:
                    self.__copyWithProgress(source_item, target_item, follow_symlinks=(r'symlinks' in self.opts))
        return True
    
    def __checkFiles(self, source, target):
        sourceInfo = source.lstat()
        targetInfo = target.lstat()
        cmpFiles = (r'fullcmp' in self.opts)

        if sourceInfo.st_mtime == targetInfo.st_mtime:
            if not(r'noconflicts' in self.opts):
                if (sourceInfo.st_size != targetInfo.st_size) or \
                   (cmpFiles and not(self.__compare2file(source, target))):
                    self.out(r'Conflict: ' + source + r' -> ' + target + r' (equal modification time files with different content)', False)
                    self.__copyWithProgress(source, target.with_suffix(r'.conflict.' + self.hub), follow_symlinks=(r'symlinks' in self.opts))
            return

        if sourceInfo.st_mtime < targetInfo.st_mtime:
            return

        if sourceInfo.st_size != targetInfo.st_size or not(cmpFiles) or not(self.__compare2file(source, target)):
            self.__copyWithProgress(source, target, follow_symlinks=(r'symlinks' in self.opts))