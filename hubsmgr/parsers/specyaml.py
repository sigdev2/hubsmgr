#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml

class SpecYamlParser:
    __slots__ = ()

    def parse(self, parsers, file):
        self.__recParse(parsers, yaml.safe_load(file), r'', r'')

    def __recParse(self, parsers, data, path, node):
        for parser in (parsers if len(path) > 0 else []):
            if parser.check(path) and parser.process(data, node):
                return
        for dataKey in (data
                        if isinstance(data, dict)
                        else (range(data) if isinstance(data, list) else [])):
            self.__recParse(parsers, data[dataKey], path + r'/' + str(dataKey), str(dataKey))
