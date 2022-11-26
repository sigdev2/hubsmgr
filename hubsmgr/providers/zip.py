#!/usr/bin/env python
# -*- coding: utf-8 -*-

from providers.provider import Provider
import zipfile
import shutil
import pathlib

class Zip(Provider):
    def __init__(self, hub, name, url, root, out = None):
        super(Zip, self).__init__(hub, name, url, root, out)
    
    def updateRemotes(self):
        return 0
        
    def isExist(self):
        p = self.path()
        z = p.with_suffix(r'.zip')
        return (p.exists() and p.is_dir()) or (z.exists() and zipfile.is_zipfile(z))

    def commit(self, message, addAll):
        return 0

    def pull(self):
        self.__comparePaths(pathlib.Path(self.url), self.path())
        return 0
    
    def push(self):
        self.__comparePaths(self.path(), pathlib.Path(self.url))
        return 0
    
    def clone(self):
        source_path = pathlib.Path(self.url)
        source_path_zip = source_path.with_suffix(r'.zip')
        target_path_zip = self.path().with_suffix(r'.zip')

        if source_path_zip.exists() and zipfile.is_zipfile(source_path_zip):
            self.__compareZipZip(source_path_zip, target_path_zip)
        elif source_path.exists() and source_path.is_dir():
            self.__compareFolderZip(source_path_zip, target_path_zip)
        else:
            return 1
        return 0
    
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
    
    def __comparePaths(self, source_path, target_path):
        source_path_zip = source_path.with_suffix(r'.zip')
        target_path_zip = target_path.with_suffix(r'.zip')

        sourceFolder = source_path.exists() and source_path.is_dir()
        sourceZip = source_path_zip.exists() and zipfile.is_zipfile(source_path_zip)
        targetFolder = target_path.exists() and target_path.is_dir()
        targetZip = target_path_zip.exists() and zipfile.is_zipfile(target_path_zip)

        if sourceZip and targetZip:
            self.__compareZipZip(source_path_zip, target_path_zip)
        elif sourceFolder and targetZip:
            self.__compareFolderZip(source_path, target_path_zip)
        elif sourceZip and targetFolder:
            self.__compareZipFolder(source_path_zip, target_path)
    
    def __compareZipZip(self, source, target):
        with zipfile.ZipFile(source, r'r') as source_zip:
            with zipfile.ZipFile(target, r'a' + (r'r' if target.exists() else r'')) as target_zip:
                self.__compareZip(pathlib.Path(source_zip), pathlib.Path(target_zip))
    
    def __compareFolderZip(self, source, target):
        with zipfile.ZipFile(target, r'a' + (r'r' if target.exists() else r'')) as target_zip:
            self.__compareZip(source, pathlib.Path(target_zip))
    
    def __compareZipZip(self, source, target):
        with zipfile.ZipFile(source, r'r') as source_zip:
            self.__compareZip(pathlib.Path(source_zip), target)

    def __compareZip(self, source, target):
        for source_item in source.iterdir():
            target_item = target / source_item.name
            if target_item.exists():
                if source_item.is_dir():
                    self.__compareZip(source_item, target_item)
                else:
                    if source_item.lstat().st_mtime > target_item.lstat().st_mtime:
                        if not(r'fullcmp' in self.opts) or not(self.__compare2file(source_item, target_item)):
                            self.__copyWithProgress(source_item, target_item)
            else:
                if source_item.is_dir():
                    shutil.copytree(source_item, target_item, copy_function=lambda src, dst, *args, follow_symlinks=True: self.__copyWithProgress(src, dst, *args, follow_symlinks=follow_symlinks))
                else:
                    self.__copyWithProgress(source_item, target_item)
        return True