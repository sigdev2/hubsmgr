#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tararchive import TarArchive
from ziparchive import ZipArchive

def getFormatClass(path):
    if ZipArchive.isSupported(path):
        return ZipArchive
    elif TarArchive.isSupported(path):
        return TarArchive
    return None

def isSupportedArchive(path):
    return ZipArchive.isSupported(path) or TarArchive.isSupported(path)
