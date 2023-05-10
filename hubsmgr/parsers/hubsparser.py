#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import parserutils
from parseitem import ParseItem

class HubsParser:
    __slots__ = (r'hubs')

    HUBS_KETWORDS = { r'providers': [r'git', r'pysync'],
                      r'options': [r'pull', r'push', r'freeze', r'managed'] }
    HUBS_CHECK_RX = re.compile(r'^/hubs/[A-z_-]+')

    def __init__(self):
        self.hubs = dict()

    def check(self, path):
        return HubsParser.HUBS_CHECK_RX.match(path)

    def process(self, hubList, hubName):
        hubList = parserutils.parseSet(hubList)
        parameters = parserutils.parseKeywords(hubList, HubsParser.HUBS_KETWORDS, r'paths')
        if (len(parameters[r'paths']) > 0) and len(parameters[r'providers']) > 0:
            self.hubs[hubName] = ParseItem(hubName, parameters)
        return True
