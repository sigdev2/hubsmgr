#!/usr/bin/env python
# -*- coding: utf-8 -*-

import parserutils
import re
from parseitem import ParseItem

class ShortsParser:
    __slots__ = [r'shorts']

    SHORTS_CHECK_RX = re.compile(r'^/shorts/[A-z_-]+')

    def __init__(self):
        self.shorts = dict()
    
    def check(self, path):
        return ShortsParser.SHORTS_CHECK_RX.match(path)

    def process(self, shortParams, shortName):
        shortParams = parserutils.parseSet(shortParams)
        if len(shortParams) > 0:
            self.shorts[shortName] = ParseItem(shortName, shortParams)
        return True
