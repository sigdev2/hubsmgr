#!/usr/bin/env python
# -*- coding: utf-8 -*-

def parseSet(item):
    itemType = type(item)
    if itemType == list:
        return set(item)
    if itemType == str:
        return set(item.split())
    return set()

def parseKeywords(args, keywords, residue):
    parameters = dict()
    for part in keywords:
        finded = args.intersection(keywords[part])
        if len(finded) != 0:
            args = args.difference(finded)
        parameters[part] = finded
    parameters[residue] = args
    return parameters