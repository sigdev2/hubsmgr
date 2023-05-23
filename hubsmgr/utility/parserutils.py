#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

PROJECT_NAME_RX = re.compile(r'^([^{]*){{([^}]+)}}(.*)$')

def parseSet(item):
    itemType = type(item)
    if itemType == list:
        return set(item)
    if itemType == str:
        return set(item.split())
    return set()

def parseKeywords(args, keywords, residue):
    parameters = {}
    for part in keywords:
        finded = args.intersection(keywords[part])
        if len(finded) != 0:
            args = args.difference(finded)
        parameters[part] = finded
    parameters[residue] = args
    return parameters

def parseProjectNameParts(name):
    parts = name.split(r'@', 1)
    if len(parts) < 2:
        parts.insert(0, r'')
    parts = parts[1].split(r'@', 1)
    matches = PROJECT_NAME_RX.finditer(parts[1])
    for _, match in enumerate(matches, start=1):
        before = match.group(1)
        project = match.group(2)
        after = match.group(3)
        parts[1] = project
        parts.append(before + project + after)
        return parts
    parts.append(parts[1])
    return parts
