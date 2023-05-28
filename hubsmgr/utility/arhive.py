#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utility import archiveutils

#todo: support iso and isz

class Archive:
    __slots__ = (r'__archive',)

    def __init__(self, path):
        archiveClass = archiveutils.getFormatClass(path)
        if archiveClass is None:
            self.__archive = None
        else:
            self.__archive = archiveClass(path)

    def isValid(self):
        return not self.__archive is None

    def unpackall(self, toPath):
        if not self.__archive is None:
            self.__archive.unpackall(toPath)

    def packall(self, fromPath):
        if not self.__archive is None:
            self.__archive.packall(fromPath)
