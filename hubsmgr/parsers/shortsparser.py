#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from parsers.parser import Parser

class ShortsParser(Parser):
    __slots__ = ()

    SHORTS_CHECK_RX = re.compile(r'^/shorts/[A-z_-0-9]+')

    def __init__(self):
        super(ShortsParser, self).__init__({}, r'shorts', ShortsParser.SHORTS_CHECK_RX)
