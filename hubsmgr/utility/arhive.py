#!/usr/bin/env python
# -*- coding: utf-8 -*-

import utility.archiveutils

#todo: support iso and isz

class Archive:
    __slots__ = (r'__archive')

    def __init__(self, path):
        archiveClass = utility.archiveutils.getFormatClass(path)
        if archiveClass == None:
            self.__archive = None
        else:
            self.__archive = archiveClass(path)
    
    def isValid(self):
        return self.__archive != None
    
    def unpackall(self, toPath):
        if self.__archive != None:
            self.__archive.unpackall(toPath)
    
    def packall(self, fromPath):
        if self.__archive != None:
            self.__archive.packall(fromPath)