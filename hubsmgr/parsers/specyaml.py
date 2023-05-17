#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
from parsers.shortsparser import ShortsParser
from parsers.projectsparser import ProjectsParser
from parsers.hubsparser import HubsParser

class SpecYamlParser:
    __slots__ = ()

    def parse(self, parsers, file):
        self.__recParse(parsers, yaml.safe_load(file), r'', r'')

    @staticmethod
    def parseconfig(config):
        shortsParser = ShortsParser()
        hubsParser = HubsParser()
        projectsParser = ProjectsParser(shortsParser.shorts, hubsParser.hubs)
        with config.open(r'r') as f:
            SpecYamlParser().parse([shortsParser, hubsParser, projectsParser], f)
        return projectsParser

    def __recParse(self, parsers, data, path, node):
        for parser in (parsers if len(path) > 0 else []):
            if parser.check(path) and parser.process(data, node):
                return
        for dataKey in (data
                        if isinstance(data, dict)
                        else (range(data) if isinstance(data, list) else [])):
            self.__recParse(parsers, data[dataKey], path + r'/' + str(dataKey), str(dataKey))
