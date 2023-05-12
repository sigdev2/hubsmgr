#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utility.tararchive import TarArchive
from utility.ziparchive import ZipArchive

def getFormatClass(path):
    if ZipArchive.isSupported(path):
        return ZipArchive
    if TarArchive.isSupported(path):
        return TarArchive
    return None

def isSupportedArchive(path):
    return ZipArchive.isSupported(path) or TarArchive.isSupported(path)
