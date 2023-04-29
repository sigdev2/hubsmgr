#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zipfile
import tarfile
import lzma
import time
import os

ARCHIVE_FORMATS = [r'.zip', r'.tar', r'.tar.gz', r'.tgz', r'.tar.bz2', r'.tar.bzip2', r'.tbz2', r'.tbzip2', r'.tar.lzma', r'.tar.xz', r'.txz', r'.tlzma', r'.iso', r'.isz']

def createInfo(archive, path):
    if isinstance(archive, tarfile.TarFile):
        info = tarfile.TarInfo(path)
        info.name = info.name.replace(r'\\', r'/')
        return info
    info = zipfile.ZipInfo(path)
    info.filename = info.name.replace(r'\\', r'/')

def createFullInfo(archive, path, fromPath):
    in_stat = os.stat(path)
    info = createInfo(archive, os.path.relpath(path, fromPath))
    seiPermisions(info, os.stat.S_IMODE(in_stat.st_mode))
    seiMTime(info, in_stat.st_mtime)
    return info

def open(path, mode):
    if path.endswith(r'.zip'):
        return (zipfile.ZipFile(path))
    elif path.endswith(r'.tar'):
        return (tarfile.open(path, mode + r':'))
    elif path.endswith(r'.tar.gz') or path.endswith(r'.tgz'):
        return (tarfile.open(path, mode + r':gz'))
    elif path.endswith(r'.tar.bz2') or path.endswith(r'.tar.bzip2') or path.endswith(r'.tbz2') or path.endswith(r'.tbzip2'):
        return (tarfile.open(path, mode + r':bz2'))
    elif path.endswith(r'.tar.lzma') or path.endswith(r'.tar.xz') or path.endswith(r'.txz') or path.endswith(r'.tlzma'):
        xz_file = lzma.LZMAFile(path, mode=mode)
        return (tarfile.open(mode=mode, fileobj=xz_file), xz_file)
    
    return None

def isSupportedArchive(path):
    isArchive = False
    for format in ARCHIVE_FORMATS:
        if path.endswith(format):
            isArchive = True
            break
    return isArchive

def addFile(archive, info, fileobj):
    if isinstance(archive, tarfile.TarFile):
        return archive.addfile(info, fileobj)
    return archive.writestr(info, fileobj.read())

def addEmptyDir(archive, info):
    if isinstance(archive, tarfile.TarFile):
        info.type = tarfile.DIRTYPE
        return archive.addfile(info)
    return archive.writestr(info, r'')

def seiPermisions(info, mode):
    if isinstance(info, tarfile.TarInfo):
        info.mode = mode
        return
    info.external_attr = mode << 16

def seiMTime(info, mtime):
    if isinstance(info, tarfile.TarInfo):
        info.mtime = mtime
        return
    info.date_time = time.localtime(mtime)