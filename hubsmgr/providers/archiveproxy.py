#!/usr/bin/env python
# -*- coding: utf-8 -*-

from providerproxy import ProviderProxy
from utility import arhive
from utility import archiveutils
import tempfile
import os
import shutil

class ArchiveProxy(ProviderProxy):
    __slots__ = [r'__packed', r'__tempdir']
    
    def __init__(self, source):
        self.__tempdir = tempfile.TemporaryDirectory()
        
        self.__packed = source
        if self.isExist():
            archive = arhive.Archive(self.__packed.path)
            todo unpack only when run first operation
            archive.unpackall(self.__tempdir)

        baseProvider = self.source.source if isinstance(self.source, ProviderProxy) else self.source
        providerClass = type(baseProvider)
        super(ArchiveProxy, self).__init__(providerClass(self.__tempdir, baseProvider.out))
    
    def isCommitSupport(self):
        return False
    
    def isValid(self):
        return archiveutils.isSupportedArchive(self.__packed.path) and self.source.isExist() and self.source.isValid()
    
    def isExist(self):
        return os.path.exists(self.__packed.path) and os.path.is_file(self.__packed.path)
    
    def commit(self, message, addAll):
        return -1

    def pull(self, remote, opts):
        todo chack changes by data
        e = super(ArchiveProxy, self).pull(remote, opts)
        if e != 0:
            return e
        return self.__pack()
        
    def push(self, remote, opts):
        todo chack changes by data
        e = super(ArchiveProxy, self).push(remote, opts)
        if e != 0:
            return e
        return self.__pack()
    
    def clone(self, remote, opts):
        e = super(ArchiveProxy, self).clone(remote, opts)
        if e != 0:
            return e
        return self.__pack()
    
    def __pack(self):
        file = tempfile.TemporaryFile()
        archive = arhive.Archive(file)
        archive.packall(file)
        if os.path.exists(self.__packed.path):
            os.remove(self.__packed.path)
        shutil.copy(file, self.__packed.path)
        return 0