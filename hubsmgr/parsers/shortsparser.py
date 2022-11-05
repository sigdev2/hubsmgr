#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

class Short:
    __slots__ = [r'params', r'id']

    def __init__(self, id, params):
        self.id = id
        self.params = params

class ShortsParser:
    __slots__ = [r'shorts']

    def __init__(self):
        self.shorts = dict()
    
    def check(self, path):
        return re.match(r'^/shorts/[A-z_-]+', path)

    def process(self, shortParams, shortName):
        if not(type(shortParams) is list):
            shortParams = shortParams.split()
        if len(shortParams) != 0:
            self.shorts[shortName] = Short(shortName, set(shortParams))
        return True
