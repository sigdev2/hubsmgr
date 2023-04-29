#!/usr/bin/env python
# -*- coding: utf-8 -*-

from providerproxy import ProviderProxy
import tempfile
import zipfile
import tarfile
import lzma
import bz2
import os

def openArchive(path, mode):
    if path.endswith(r'.zip'):
        return zipfile.ZipFile(path)
    elif path.endswith(r'.tar'):
        return tarfile.open(path, mode + r':')
    elif path.endswith(r'.tar.gz') or path.endswith(r'.tgz'):
        return tarfile.open(path, mode + r':gz')
    elif path.endswith(r'.tar.bz2') or path.endswith(r'.tar.bzip2') or path.endswith(r'.tbz2') or path.endswith(r'.tbzip2'):
        return tarfile.open(path, mode + r':bz2')
    elif path.endswith(r'.tar.lzma') or path.endswith(r'.tar.xz') or path.endswith(r'.txz') or path.endswith(r'.tlzma'):
        xz_file = lzma.LZMAFile(path, mode=mode)
        return tarfile.open(mode=mode, fileobj=xz_file)

#todo: support iso and isz
class ArchiveProxy(ProviderProxy):
    __slots__ = [r'__packed', r'__tempdir']
    
    def __init__(self, source):
        self.__tempdir = tempfile.TemporaryDirectory()
        
        self.__packed = source
        todo store dates
        if self.isExist():
            if source.path.endswith(r'.zip'):
                zip = zipfile.ZipFile(source.path)
                zip.extractall(self.__tempdir)
                zip.close()
            elif source.path.endswith(r'.tar'):
                tar = tarfile.open(source.path, r'r:')
                tar.extractall(self.__tempdir)
                tar.close()
            elif source.path.endswith(r'.tar.gz') or source.path.endswith(r'.tgz'):
                tar = tarfile.open(source.path, r'r:gz')
                tar.extractall(self.__tempdir)
                tar.close()
            elif source.path.endswith(r'.tar.bz2') or source.path.endswith(r'.tar.bzip2') or source.path.endswith(r'.tbz2') or source.path.endswith(r'.tbzip2'):
                tar = tarfile.open(source.path, r'r:bz2')
                tar.extractall(self.__tempdir)
                tar.close()
            elif source.path.endswith(r'.tar.lzma') or source.path.endswith(r'.tar.xz') or source.path.endswith(r'.txz') or source.path.endswith(r'.tlzma'):
                xz_file = lzma.LZMAFile(source.path, mode=r'r')
                tar = tarfile.open(mode=r'r', fileobj=xz_file)
                tar.extractall(self.__tempdir)
                tar.close()
                xz_file.close()

        baseProvider = self.source.source if isinstance(self.source, ProviderProxy) else self.source
        providerClass = type(baseProvider)
        super(ArchiveProxy, self).__init__(providerClass(self.__tempdir, baseProvider.out))
    
    def isCommitSupport(self):
        return False
    
    def isExist(self):
        return os.path.exists(self.__packed.path) and os.path.is_file(self.__packed.path)
    
    def commit(self, message, addAll):
        return -1

    def pull(self, remote, opts):
        e = super(ArchiveProxy, self).pull(remote, opts)
        if e != 0:
            return e
        return self.__pack()
        
    def push(self, remote, opts):
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
        todo store dates
        
        z = zipfile.ZipFile(zip_fname, "w", compression=zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(in_dir):
            for file in files:
                in_fname = os.path.join(root, file)
                in_stat = os.stat(in_fname)
                info = zipfile.ZipInfo(in_fname)
                info.filename = os.path.relpath(in_fname, in_dir)
                if os.path.sep == "\\":
                    info.filename = os.path.relpath(in_fname, in_dir).replace("\\", "/")
                info.date_time = time.localtime(in_stat.st_mtime)
                perms = stat.S_IMODE(in_stat.st_mode) | stat.S_IFREG
                info.external_attr = perms << 16
                with open_readable(in_fname, "rb") as fobj:
                    contents = fobj.read()
                z.writestr(info, contents, zipfile.ZIP_DEFLATED)
            pass
        z.close()

        return -1