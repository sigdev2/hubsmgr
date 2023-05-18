#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from parsers.parser import Parser

class HubsParser(Parser):
    __slots__ = ()

    HUBS_CHECK_RX = re.compile(r'^/hubs/[A-z_\-0-9]+')

    def __init__(self):
        super(HubsParser, self).__init__({ r'providers': (r'git', r'pysync'),
                                           r'options': (r'pull', r'push', r'freeze', r'managed') },
                                         r'paths', HubsParser.HUBS_CHECK_RX)

    def validate(self, parameters):
        return (len(parameters[r'paths']) > 0) and len(parameters[r'providers']) > 0
