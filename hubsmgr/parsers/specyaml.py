#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
from parsers.shortsparser import ShortsParser # pylint: disable=import-error disable=no-name-in-module
from parsers.projectsparser import ProjectsParser
from parsers.hubsparser import HubsParser # pylint: disable=import-error disable=no-name-in-module

class SpecYamlParser:
    __slots__ = ()

    def parse(self, parsers, file):
        self.__recParse(parsers, yaml.safe_load(file), r'', r'')

    @staticmethod
    def parseconfig(config):
        shortsParser = ShortsParser()
        hubsParser = HubsParser()
        projectsParser = ProjectsParser(shortsParser.items, hubsParser.items)
        with config.open(r'r') as f:
            SpecYamlParser().parse((shortsParser, hubsParser, projectsParser), f)
        return projectsParser

    def __recParse(self, parsers, data, path, node):
        for parser in (parsers if len(path) > 0 else []):
            if parser.check(path) and parser.process(data, node):
                return
        for dataKey in (data if isinstance(data, dict) else
                        (range(len(data)) if isinstance(data, list) else
                         [])):
            self.__recParse(parsers, data[dataKey], path + r'/' + str(dataKey), str(dataKey))
