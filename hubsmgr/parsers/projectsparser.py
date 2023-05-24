#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from utility import parserutils
from parsers.parser import Parser
from parsers.parseitem import ParseItem

class ProjectsParser(Parser):
    __slots__ = (r'projects', r'__shorts', r'__hubs')

    PROJECT_CHECK_RX = re.compile(r'^(?!/hubs|/shorts)/[A-z_\-0-9]+')

    def __init__(self, shorts, hubs):
        self.__shorts = shorts
        self.__hubs = hubs
        super().__init__(
            { r'sync': (r'pull', r'push', r'freeze', r'autocommit'),
              r'hubs' : self.__hubs.keys() },
            r'options', ProjectsParser.PROJECT_CHECK_RX)

    def countHubs(self):
        return len(self.__hubs)

    def process(self, data, node):
        project = parserutils.parseSet(data)
        if len(project) <= 0:
            return False
        parameters = self.parseKeywords(self.__unpack(project, set()))
        hubsKeys = parameters[r'hubs']
        hubs = tuple(self.__hubs[key] for key in hubsKeys if key in self.__hubs)
        if len(hubs) > 0:
            parameters[r'hubs'] = hubs
            auth, name, target = parserutils.parseProjectNameParts(node)
            parameters[r'auth'] = auth
            parameters[r'target'] = target
            self.items[name] = ParseItem(name, parameters)
        return True

    def __unpack(self, keys, vis):
        return { sub for key in keys if not key in vis
                     for sub in (self.__unpack(self.__shorts[key].parameters[r'short'], vis.union({key}))
                                 if key in self.__shorts
                                 else (key,)) }
