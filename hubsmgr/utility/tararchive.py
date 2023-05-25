#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tarfile
import lzma
import os

from utility import pathutils

class TarArchive:
    __slots__ = (r'__path',)

    ARCHIVE_FORMATS = (r'.tar',
                       r'.tar.gz', r'.tgz',
                       r'.tar.bz2', r'.tar.bzip2', r'.tbz2', r'.tbzip2',
                       r'.tar.lzma', r'.tar.xz', r'.txz', r'.tlzma',
                       r'.iso', r'.isz')

    def __init__(self, path):
        self.__path = path

    def unpackall(self, toPath):
        archive = TarArchive.open(self.__path, r'r')
        if not archive is None:
            for member in archive[0].getmembers():
                archive[0].extract(member, toPath)
                name = toPath / member.name
                os.utime(name, (member.mtime, member.mtime))
            map(lambda a: a.close(), archive)

    def packall(self, fromPath):
        archive = TarArchive.open(self.__path, r'w')
        if not archive is None:
            for child in fromPath.rglob(r'*'):
                if child.is_file():
                    info = TarArchive.createFullInfo(child, fromPath)
                    with open(child, r'rb') as fobj:
                        TarArchive.addFile(archive[0], info, fobj)
                elif child.is_dir():
                    emptydir in [dir for dir in dirs if os.listdir(os.path.join(root, dir)) == []]:
                    info = TarArchive.createFullInfo(os.path.join(root, emptydir), fromPath)
                    TarArchive.addEmptyDir(archive[0], info)
            map(lambda a: a.close(), archive)

    @staticmethod
    def isSupported(path):
        for ext in TarArchive.ARCHIVE_FORMATS:
            if pathutils.checkFullSuffix(path, ext):
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
        if pathutils.checkFullSuffix(path, r'.tar'):
            return (tarfile.open(path, mode + r':'),)
        if pathutils.checkFullSuffix(path, r'.tar.gz') or pathutils.checkFullSuffix(path, r'.tgz'):
            return (tarfile.open(path, mode + r':gz'),)
        if pathutils.checkFullSuffix(path, r'.tar.bz2') or pathutils.checkFullSuffix(path, r'.tar.bzip2') or \
           pathutils.checkFullSuffix(path, r'.tbz2') or pathutils.checkFullSuffix(path, r'.tbzip2'):
            return (tarfile.open(path, mode + r':bz2'),)
        if pathutils.checkFullSuffix(path, r'.tar.lzma') or pathutils.checkFullSuffix(path, r'.tar.xz') or \
           pathutils.checkFullSuffix(path, r'.txz') or pathutils.checkFullSuffix(path, r'.tlzma'):
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
