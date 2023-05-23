#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import pathlib

PATH_RX = re.compile(r'^([A-z]+\:\/{1,2}|[A-z]+\:|\/{1}|\\{1}|\.{1,2})?\/|\\')
URL_RX = re.compile(r'^([A-z]+):\/\/')

def isUrl(path):
    match = URL_RX.search(str(path))
    if match is None:
        return False
    protocol = match.group(1)
    return not protocol in (r'file', r'windrives')

def checkFullSuffix(path, suffix):
    return r''.join(path.suffixes) == suffix

def __isChildPathOrSame(path, root):
    return path == root or path.is_relative_to(root)

def __normalizePathEnding(path, sep = r'/'):
    if path[-1] != sep:
        if (sep == r'/' and path[-1] == r'\\') or (sep == r'\\' and path[-1] == r'/'):
            path[-1] = sep
        else:
            path += sep
    return path

def __replaceProjectPathTemplate(path, target, sep = os.sep):
    newPath = path.replace(r'{{project}}', target, 1)
    if newPath == path:
        newPath = __normalizePathEnding(newPath, sep) + target + sep
    return newPath

def __createAbsolutePath(path, target):
    return pathlib.Path(__replaceProjectPathTemplate(path, target)).resolve()

def unpackSyncPaths(paths, target, relative):
    out = set()
    for path in paths:
        path = path.strip()

        match = PATH_RX.search(str(path))
        if not match is None:
            protocol = match.group(1)
            if protocol.endswith(r':/'):
                out.add(__replaceProjectPathTemplate(path.strip(), target, r'/'))
            elif protocol == r'file://':
                absPath = __createAbsolutePath(path[len(protocol):], target)
                if not __isChildPathOrSame(absPath, relative) and absPath.exists():
                    out.add(absPath)
            elif protocol == r'windrives:/':
                corePath = path[len(protocol):]
                for subpath in [ x + r':/' + corePath for x in r'QWERTYUIOPASDFGHJKLZXCVBNM' ]:
                    absPath = __createAbsolutePath(subpath, target)
                    if not __isChildPathOrSame(absPath, relative) and absPath.exists():
                        out.add(absPath)
            elif protocol in (r'.', r'..'):
                absPath = __createAbsolutePath(path, target)
                if not __isChildPathOrSame(absPath, relative) and absPath.exists():
                    out.add(absPath)
    return out

def yamlpaths(path):
    paths = []
    path = path.resolve()
    if path.is_dir():
        paths = [f for ext in (r'*.yaml', r'*.yml') for f in path.glob(ext)]
    elif path.is_file():
        paths.append(path)
    return paths

def configdir(config):
    rootPath = config.parent / config.stem
    if not rootPath.exists() or not rootPath.is_dir():
        rootPath.mkdir()
    if not rootPath.exists():
        return False
    return rootPath
