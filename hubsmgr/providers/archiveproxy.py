#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
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
        baseProvider = self.source.source if isinstance(self.source, ProviderProxy) else self.source
        providerClass = type(baseProvider)
        super().__init__(providerClass(self.__tempdir, baseProvider.out))

    def isCommitSupport(self):
        return False

    def isValid(self):
        return archiveutils.isSupportedArchive(self.__packed.path) and self.source.isValid()

    def isExist(self):
        return os.path.exists(self.__packed.path) and os.path.isfile(self.__packed.path)

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
        tempdir = pathlib.Path(self.__tempdir)
        dirmtime = max([tempdir.joinpath(root).joinpath(f).stat().st_mtime
                        for root, _, files in os.walk(tempdir)
                        for f in files])
        archivemtime = pathlib.Path(self.__packed.path).stat().st_mtime
        if archivemtime == dirmtime:
            return 0
        if archivemtime > dirmtime:
            return -1

        self.source.out(r'Pack ' + str(self.__tempdir) + r' -> ' + str(self.__packed.path), False)
        file = tempfile.TemporaryFile()
        archive = arhive.Archive(file)
        archive.packall(self.__tempdir)
        if os.path.exists(self.__packed.path):
            os.remove(self.__packed.path)
        shutil.copy(file, self.__packed.path)
        return 0

    def __unpack(self):
        if not self.isExist() or self.__unpacked:
            return
        # todo: reading archive without unpacking or unpack in memory (is acceptable size)
        self.source.out(r'Unpack ' + str(self.__packed.path) + r' -> ' + str(self.__tempdir), False)
        archive = arhive.Archive(self.__packed.path)
        archive.unpackall(self.__tempdir)
        self.__unpacked = True
