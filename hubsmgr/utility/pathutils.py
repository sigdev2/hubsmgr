#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import pathlib

PATH_RX = re.compile(r'^([A-z]+\:\/{1,2}|[A-z]+\:|\/{1}|\\{1}|\.{1,2})?\/|\\')
URL_RX = re.compile(r'^([A-z]+):\/\/')

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

def isUrl(path):
    match = URL_RX.search(path)
    if match is None:
        return False
    protocol = match.group(1)
    return not protocol in (r'file', r'windrives')

def isChildPathOrSame(path, root):
    return path == root or pathlib.Path(path).is_relative_to(root)

def unpackSyncPaths(paths, target, relative):
    out = set()
    relative = os.path.abspath(normalizePathEnding(relative.strip()))
    for path in paths:
        path = normalizePathEnding(path.strip())
        path = generateFullPath(path, target)

        match = PATH_RX.search(path)
        if not match is None:
            protocol = match.group(1)
            if protocol.endswith(r':/'):
                out.add(path)
            elif protocol == r'file://':
                absPath = os.path.abspath(path[len(protocol):])
                if not isChildPathOrSame(absPath, relative) and os.path.exists(absPath):
                    out.add(absPath)
            elif protocol == r'windrives:/':
                corePath = path[len(protocol):]
                for subpath in [ x + r':/' + corePath for x in r'QWERTYUIOPASDFGHJKLZXCVBNM' ]:
                    absPath = os.path.abspath(subpath)
                    if not isChildPathOrSame(absPath, relative) and os.path.exists(absPath):
                        out.add(absPath)
            elif protocol in (r'.', r'..'):
                absPath = os.path.abspath(path)
                if not isChildPathOrSame(absPath, relative) and os.path.exists(absPath):
                    out.add(absPath)
    return out
