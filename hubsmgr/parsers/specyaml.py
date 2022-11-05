#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml

class SpecYamlParser:
    __slots__ = [r'__file', r'__parsers']

    def __init__(self, file):
        self.__file = file
        self.__parsers = []

    def addParser(self, parser):
        self.__parsers.append(parser)

    def parse(self):
        self.__recParse(yaml.safe_load(self.__file), r'', r'')
    
    def __recParse(self, data, path, node):
        if len(path) > 0:
            for parser in self.__parsers:
                if parser.check(path):
                    if parser.process(data, node):
                        return

        if isinstance(data, dict):
            for dataKey in data:
                self.__recParse(data[dataKey], path + r'/' + dataKey, dataKey)
        elif isinstance(data, list):
            for index in range(data):
                self.__recParse(data[index], path + r'/' + str(index), str(index))