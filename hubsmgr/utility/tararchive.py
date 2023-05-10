#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tarfile
import lzma
import os

class TarArchive:
    __slots__ = (r'__path')

    ARCHIVE_FORMATS = (r'.tar', r'.tar.gz', r'.tgz', r'.tar.bz2', r'.tar.bzip2', r'.tbz2', r'.tbzip2', r'.tar.lzma', r'.tar.xz', r'.txz', r'.tlzma', r'.iso', r'.isz')

    def __init__(self, path):
        self.__path = path
    
    def unpackall(self, toPath):
        archive = TarArchive.open(self.__path, r'r')
        if archive != None:
            for member in archive[0].getmembers():
                archive[0].extract(member, toPath)
                name = os.path.join(toPath, member.name)
                os.utime(name, (member.mtime, member.mtime))
            map(lambda a: a.close(), archive)

    def packall(self, fromPath):
        archive = TarArchive.open(self.__path, r'w')
        if archive != None:
            for root, dirs, files in os.walk(fromPath):
                for file in files:
                    in_fname = os.path.join(root, file)
                    info = TarArchive.createFullInfo(in_fname, fromPath)
                    with open(in_fname, r'rb') as fobj:
                        TarArchive.addFile(archive[0], info, fobj)
                for emptydir in [dir for dir in dirs if os.listdir(os.path.join(root, dir)) == []]:
                    info = TarArchive.createFullInfo(os.path.join(root, emptydir), fromPath)
                    TarArchive.addEmptyDir(archive[0], info)
            map(lambda a: a.close(), archive)
            
    @staticmethod
    def isSupported(path):
        for format in TarArchive.ARCHIVE_FORMATS:
            if path.endswith(format):
                return True
        return False

    @staticmethod
    def createInfo(path):
        info = tarfile.TarInfo(path)
        info.name = info.name.replace(r'\\', r'/')
        return info

    @staticmethod
    def createFullInfo(path, fromPath):
        in_stat = os.stat(path)
        info = TarArchive.createInfo(os.path.relpath(path, fromPath))
        TarArchive.seiPermisions(info, os.stat.S_IMODE(in_stat.st_mode))
        TarArchive.seiMTime(info, in_stat.st_mtime)
        return info

    @staticmethod
    def open(path, mode):
        if path.endswith(r'.tar'):
            return (tarfile.open(path, mode + r':'))
        elif path.endswith(r'.tar.gz') or path.endswith(r'.tgz'):
            return (tarfile.open(path, mode + r':gz'))
        elif path.endswith(r'.tar.bz2') or path.endswith(r'.tar.bzip2') or path.endswith(r'.tbz2') or path.endswith(r'.tbzip2'):
            return (tarfile.open(path, mode + r':bz2'))
        elif path.endswith(r'.tar.lzma') or path.endswith(r'.tar.xz') or path.endswith(r'.txz') or path.endswith(r'.tlzma'):
            xz_file = lzma.LZMAFile(path, mode=mode)
            return (tarfile.open(mode=mode, fileobj=xz_file), xz_file)
        return None

    @staticmethod
    def addFile(archive, info, fileobj):
        return archive.addfile(info, fileobj)

    @staticmethod
    def addEmptyDir(archive, info):
        info.type = tarfile.DIRTYPE
        return archive.addfile(info)

    @staticmethod
    def seiPermisions(info, mode):
        info.mode = mode

    @staticmethod
    def seiMTime(info, mtime):
        info.mtime = mtime