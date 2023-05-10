#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

import parserutils
from parseitem import ParseItem

class ProjectsParser:
    __slots__ = (r'projects', r'shorts', r'hubs')

    PROJECT_PROPS = { r'sync': [r'pull', r'push', r'freeze', r'autocommit'] }
    PROJECT_CHECK_RX = re.compile(r'^(?!/hubs|/shorts)/[A-z_-]+')

    def __init__(self, shorts, hubs):
        self.projects = dict()
        self.shorts = shorts
        self.hubs = hubs

    def check(self, path):
        return ProjectsParser.PROJECT_CHECK_RX.match(path)

    def process(self, project, projectName):
        project = parserutils.parseSet(project)
        if len(project) > 0:
            keywords = ProjectsParser.PROJECT_PROPS
            keywords[r'hubs'] = self.hubs.keys()
            parameters = parserutils.parseKeywords(self.__unpack(project, set()),
                                                   keywords, r'options')
            hubsKeys = parameters[r'hubs']
            hubs = [self.hubs[key] for key in hubsKeys if key in self.hubs]
            parameters[r'hubs'] = hubs
            if len(hubs) > 0:
                self.projects[projectName] = ParseItem(projectName, parameters)
        return True

    def __unpack(self, keys, vis):
        return { sub for key in keys if not(key in vis)
                     for sub in (self.__unpack(self.shorts[key].params, vis.union({key}))
                                 if key in self.shorts
                                 else {key}) }
