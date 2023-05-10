#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pathlib
import shutil
import tempfile
from providerproxy import ProviderProxy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), r'../')))

from utility import arhive
from utility import archiveutils

class ArchiveProxy(ProviderProxy):
    __slots__ = (r'__packed', r'__tempdir', r'__unpacked')

    def __init__(self, source):
        self.__unpacked = False
        self.__tempdir = tempfile.TemporaryDirectory()
        self.__packed = source
        baseProvider = self.source.source if isinstance(self.source, ProviderProxy) else self.source
        providerClass = type(baseProvider)
        super(ArchiveProxy, self).__init__(providerClass(self.__tempdir, baseProvider.out))

    def isCommitSupport(self):
        return False

    def isValid(self):
        return archiveutils.isSupportedArchive(self.__packed.path) and self.source.isValid()

    def isExist(self):
        return os.path.exists(self.__packed.path) and os.path.isfile(self.__packed.path)

    def commit(self, message, addAll):
        return -1

    def pull(self, remote, opts):
        self.__unpack()
        e = super(ArchiveProxy, self).pull(remote, opts)
        if e != 0:
            return e
        return self.__pack()

    def push(self, remote, opts):
        self.__unpack()
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
        tempdir = pathlib.Path(self.__tempdir)
        dirmtime = max([tempdir.joinpath(root).joinpath(f).stat().st_mtime
                        for root, _, files in os.walk(tempdir)
                        for f in files])
        archivemtime = pathlib.Path(self.__packed.path).stat().st_mtime
        if archivemtime == dirmtime:
            return 0
        if archivemtime > dirmtime:
            return -1

        file = tempfile.TemporaryFile()
        archive = arhive.Archive(file)
        archive.packall(self.__tempdir)
        if os.path.exists(self.__packed.path):
            os.remove(self.__packed.path)
        shutil.copy(file, self.__packed.path)
        return 0

    def __unpack(self):
        if self.isExist() and not self.__unpacked:
            archive = arhive.Archive(self.__packed.path)
            archive.unpackall(self.__tempdir)
            self.__unpacked = True
