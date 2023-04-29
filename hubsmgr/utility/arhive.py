#!/usr/bin/env python
# -*- coding: utf-8 -*-

import utility.archiveutils
import os

#todo: support iso and isz
class Archive:
    __slots__ = [r'__path']

    def __init__(self, path):
        self.__path = path
    
    def extractall(self, toPath):
        archive = utility.archiveutils.__open(r'r')
        if archive != None:
            archive[0].extractall(toPath)
            map(lambda a: a.close(), archive)
    
    def packall(self, fromPath):
        archive = utility.archiveutils.open(self.__path, r'r')
        for root, dirs, files in os.walk(fromPath):
            for file in files:
                in_fname = os.path.join(root, file)
                info = utility.archiveutils.createFullInfo(archive, in_fname, fromPath)
                with open(in_fname, r'rb') as fobj:
                    utility.archiveutils.addFile(archive, info, fobj)
            for empydir in [dir for dir in dirs if os.listdir(os.path.join(root, dir)) == []]:
                info = utility.archiveutils.createFullInfo(archive, os.path.join(root, empydir), fromPath)
                utility.archiveutils.addEmpyDir(archive, info)
        archive.close()