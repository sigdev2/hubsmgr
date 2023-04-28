#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os

PATH_RX = re.compile(r'^([A-z]+\:\/{1,2}|[A-z]+\:|\/{1}|\\{1}|\.{1,2})?\/|\\')
ARCHIVE_FORMATS = [r'.zip', r'.tar', r'.tar.gz', r'.tgz', r'.tar.bz2', r'.tar.bzip2', r'.tbz2', r'.tbzip2', r'.tar.lzma', r'.tar.xz', r'.txz', r'.tlzma', r'.iso', r'.isz']

def normalizePathEnding(path):
    if path[-1] != r'/':
        if path[-1] == r'\\':
            path[-1] = r'/'
        else:
            path += r'/'
    return path

def generateFullPath(path, target):
    newPath = path.replace(r'{{project}}', target, 1)
    if newPath == path:
        newPath += target + r'/'
    return newPath

def unpackSyncPaths(paths, target, relative):
    out = set()
    relative = normalizePathEnding(relative.strip())
    for path in paths:
        path = normalizePathEnding(path.strip())
        path = generateFullPath(path, target)
        match = PATH_RX.search(path)
        if match != None:
            protocol = match.group(1)
            if protocol.endswith(r':/'):
                out.add(path)
            elif protocol == r'file://':
                out.add(os.path.abspath(path[len(protocol):]))
            elif protocol == r'windrives:/':
                corePath = path[len(protocol):]
                for subpath in [ x + r':/' + corePath for x in r'QWERTYUIOPASDFGHJKLZXCVBNM' ]:
                    out.add(os.path.abspath(subpath))
            elif protocol == r'.' or protocol == r'..':
                    out.add(relative + os.path.abspath(subpath))
    return out

def isSupportedArchive(path):
    isArchive = False
    for format in ARCHIVE_FORMATS:
        if path.endswith(format):
            isArchive = True
            break
    return isArchive