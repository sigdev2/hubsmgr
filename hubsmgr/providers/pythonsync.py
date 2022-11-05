#!/usr/bin/env python
# -*- coding: utf-8 -*-

from providers.provider import Provider
import os
import shutil
import hashlib
import pathlib

def read_in_chunks(file_object, chunk_size=1024):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def compare2file(file1, file2):
    if file1.lstat().st_mtime != file2.lstat().st_mtime:
        return False

    with file1.open('rb') as f1:
        with file2.open('rb') as f2:
            f1It = iter(lambda : f1.read(5120), r'')
            f2It = iter(lambda : f2.read(5120), r'')

            while True:
                chunck1 = next(f1It, None)
                chunck2 = next(f2It, None)
                if (chunck1 == None) or (chunck2 == None):
                    return chunck1 == chunck2
                if hashlib.md5(chunck1).hexdigest() != hashlib.md5(chunck2).hexdigest():
                    return False
            return True

def compareFolder(source, target, cmpFiles):
    for source_item in source.iterdir():
        target_item = target / source_item.name
        if target_item.exists():
            if source_item.is_dir():
                compareFolder(source_item, target_item, cmpFiles)
            else:
                if source_item.lstat().st_mtime > target_item.lstat().st_mtime:
                    if not(cmpFiles) or not(compare2file(source_item, target_item)):
                        shutil.copy2(source_item, target_item)
        else:
            if source_item.is_dir():
                shutil.copytree(source_item, target_item)
            else:
                shutil.copy2(source_item, target_item)
    return True

class PythonSync(Provider):
    def __init__(self, hub, name, url, root, out = None):
        super(PythonSync, self).__init__(hub, name, url, root, out)
    
    def updateRemotes(self):
        return 0

    def commit(self, message, addAll):
        return 0

    def pull(self):
        compareFolder(pathlib.Path(self.url), self.path(), (r'fullcmp' in self.opts))
        return 0
    
    def push(self):
        compareFolder(self.path(), pathlib.Path(self.url), (r'fullcmp' in self.opts))
        return 0
    
    def clone(self):
        compareFolder(pathlib.Path(self.url), self.path(), (r'fullcmp' in self.opts))
        return 0