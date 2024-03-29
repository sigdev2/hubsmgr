#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utility import parserutils # pylint: disable=no-name-in-module
from parsers.parseitem import ParseItem # pylint: disable=import-error disable=no-name-in-module

class Parser:
    __slots__ = (r'items', r'__props', r'__residue', r'__checkrx')

    def __init__(self, props, residue, checkrx):
        self.items = {}
        self.__props = props
        self.__residue = residue
        self.__checkrx = checkrx

    def check(self, path):
        return self.__checkrx.match(path)

    def process(self, data, node):
        data = parserutils.parseSet(data)
        if len(data) > 0:
            parameters = self.parseKeywords(data)
            if self.validate(parameters):
                self.items[node] = ParseItem(node, parameters)
        return True

    def parseKeywords(self, data):
        return parserutils.parseKeywords(data, self.__props, self.__residue)

    def validate(self, parameters): # pylint: disable=unused-argument
        return True
