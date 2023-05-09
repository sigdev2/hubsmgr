#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zipfile
import time
import os

class ZipArchive:
    __slots__ = [r'__path']

    def __init__(self, path):
        self.__path = path
    
    def unpackall(self, toPath):
        archive = ZipArchive.open(self.__path, r'r')
        if archive != None:
            for f in archive.infolist():
                name, date_time = f.filename, f.date_time
                name = os.path.join(toPath, name)
                with open(name, r'wb') as outFile:
                    outFile.write(archive.open(f).read())
                date_time = time.mktime(date_time + (0, 0, -1))
                os.utime(name, (date_time, date_time))
            archive.close()

    def packall(self, fromPath):
        archive = ZipArchive.open(self.__path, r'w')
        if archive != None:
            for root, dirs, files in os.walk(fromPath):
                for file in files:
                    in_fname = os.path.join(root, file)
                    info = ZipArchive.createFullInfo(in_fname, fromPath)
                    with open(in_fname, r'rb') as fobj:
                        ZipArchive.addFile(archive, info, fobj)
                for emptydir in [dir for dir in dirs if os.listdir(os.path.join(root, dir)) == []]:
                    info = ZipArchive.createFullInfo(os.path.join(root, emptydir), fromPath)
                    ZipArchive.addEmptyDir(archive, info)
            archive.close()
    
    @staticmethod
    def isSupported(path):
        return path.endswith(r'zip')

    @staticmethod
    def createInfo(path):
        info = zipfile.ZipInfo(path)
        info.filename = info.filename.replace(r'\\', r'/')
        return info

    @staticmethod
    def createFullInfo(path, fromPath):
        in_stat = os.stat(path)
        info = ZipArchive.createInfo(os.path.relpath(path, fromPath))
        ZipArchive.seiPermisions(info, os.stat.S_IMODE(in_stat.st_mode))
        ZipArchive.seiMTime(info, in_stat.st_mtime)
        return info

    @staticmethod
    def open(path, mode):
        if path.endswith(r'.zip'):
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