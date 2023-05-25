#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib
import shutil
import tempfile

from utility import arhive, archiveutils
from providers.providerproxy import ProviderProxy

class ArchiveProxy(ProviderProxy):
    __slots__ = (r'__packed', r'__tempdir', r'__unpacked')

    def __init__(self, source):
        self.__unpacked = False
        self.__tempdir = tempfile.TemporaryDirectory()
        self.__packed = source
        providerClass = self.baseType()
        super().__init__(providerClass(pathlib.Path(self.__tempdir), self.out))

    def __getattr__(self, name):
        if name in ArchiveProxy.__slots__:
            return object.__getattribute__(self, name)
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name in ArchiveProxy.__slots__:
            return object.__setattr__(self, name, value)
        return super().__setattr__(name, value)

    def isCommitSupport(self):
        return False

    def isValid(self):
        return archiveutils.isSupportedArchive(self.__packed.path) and self.source.isValid()

    def isExist(self):
        return self.__packed.path.is_exists() and self.__packed.path.is_file()

    def commit(self, message, addAll): # pylint: disable=unused-argument
        return -1

    def pull(self, remote, opts):
        self.__unpack()
        e = ProviderProxy.pull(self, remote, opts)
        if e != 0:
            return e
        return self.__pack()

    def push(self, remote, opts):
        self.__unpack()
        e = ProviderProxy.push(self, remote, opts)
        if e != 0:
            return e
        return self.__pack()

    def clone(self, remote, opts):
        e = ProviderProxy.clone(self, remote, opts)
        if e != 0:
            return e
        return self.__pack()

    def __pack(self):
        if self.__packed.path.exists():
            dirmtime = max((self.source.path / file).stat().st_mtime for file in self.source.path.rglob(r'*'))
            archivemtime = self.__packed.path.stat().st_mtime
            if archivemtime == dirmtime:
                return 0
            if archivemtime > dirmtime:
                return -1
        else:
            parentDir = self.__packed.path.parent
            if not parentDir.exists() or not parentDir.is_dir():
                parentDir.mkdir(parents=True)

        self.source.out(r'Pack ' + str(self.source.path) + r' -> ' + str(self.__packed.path), False)
        with tempfile.TemporaryFile() as file:
            archive = arhive.Archive(pathlib.Path(file))
            archive.packall(self.source.path)
            if self.__packed.path.exists():
                self.__packed.path.unlink()
            shutil.copy(file, self.__packed.path)
        return 0

    def __unpack(self):
        if not self.isExist() or self.__unpacked:
            return
        self.source.out(r'Unpack ' + str(self.__packed.path) + r' -> ' + str(self.source.path), False)
        archive = arhive.Archive(self.__packed.path)
        archive.unpackall(self.source.path)
        self.__unpacked = True
