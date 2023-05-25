#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zipfile
import time
import os

from utility import pathutils

class ZipArchive:
    __slots__ = (r'__path',)

    def __init__(self, path):
        self.__path = path

    def unpackall(self, toPath):
        archive = ZipArchive.open(self.__path, r'r')
        if not archive is None:
            for f in archive.infolist():
                name, date_time = f.filename, f.date_time
                name = toPath / name
                with open(name, r'wb') as outFile:
                    with archive.open(f) as content:
                        outFile.write(content.read())
                date_time = time.mktime(date_time + (0, 0, -1))
                os.utime(name, (date_time, date_time))
            archive.close()

    def packall(self, fromPath):
        archive = ZipArchive.open(self.__path, r'w')
        if not archive is None:
            for child in fromPath.rglob(r'*'):
                if child.is_file():
                    info = ZipArchive.createFullInfo(child, fromPath)
                    with open(fromPath / child, r'rb') as fobj:
                        ZipArchive.addFile(archive, info, fobj)
                elif child.is_dir() and not any(child.iterdir()):
                    info = ZipArchive.createFullInfo(child, fromPath)
                    ZipArchive.addEmptyDir(archive, info)
            archive.close()

    @staticmethod
    def isSupported(path):
        return pathutils.checkFullSuffix(path, r'zip')

    @staticmethod
    def createInfo(path):
        info = zipfile.ZipInfo(path)
        info.filename = info.filename.replace(r'\\', r'/')
        return info

    @staticmethod
    def createFullInfo(relpath, fromPath):
        in_stat = (fromPath / relpath).stat()
        info = ZipArchive.createInfo(relpath)
        ZipArchive.seiPermisions(info, os.stat.S_IMODE(in_stat.st_mode))
        ZipArchive.seiMTime(info, in_stat.st_mtime)
        return info

    @staticmethod
    def open(path, mode):
        if pathutils.checkFullSuffix(path, r'.zip'):
            return zipfile.ZipFile(path, mode)
        return None

    @staticmethod
    def addFile(archive, info, fileobj):
        return archive.writestr(info, fileobj.read())

    @staticmethod
    def addEmptyDir(archive, info):
        return archive.writestr(info, r'')

    @staticmethod
    def seiPermisions(info, mode):
        info.external_attr = mode << 16

    @staticmethod
    def seiMTime(info, mtime):
        info.date_time = time.localtime(mtime)
