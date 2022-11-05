#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

class Project:
    __slots__ = [r'name', r'syncParams', r'hubs', r'opts']

    def __init__(self, name, syncParams, hubs, opts):
        self.name = name
        self.syncParams = syncParams
        self.hubs = hubs
        self.opts = opts

class ProjectsParser:
    __slots__ = [r'projects', r'shorts', r'hubs']

    PROJECT_PROPS = set([r'pull', r'push', r'freeze', r'autocommit'])

    def __init__(self, shorts, hubs):
        self.projects = dict()
        self.shorts = shorts
        self.hubs = hubs

    def check(self, path):
        return re.match(r'^(?!/hubs|/shorts)/[A-z_-]+', path)

    def process(self, project, projectName):
        if not(type(project) is str) and not(type(project) is list):
            return False
        if type(project) is str:
            project = project.split()

        project = set(self.__parseShortsKeys(set(project)))
        
        syncParams = project.intersection(ProjectsParser.PROJECT_PROPS)
        if len(syncParams) == 0:
            syncParams = set([r'pull', r'push'])
        project -= syncParams

        hubsKeys = project.intersection(set(self.hubs.keys()))
        if len(hubsKeys) == 0:
            return True
        project -= hubsKeys

        hubs = []
        for key in hubsKeys:
            hubs.append(self.hubs[key])
        
        self.projects[projectName] = Project(projectName, syncParams, hubs, project)
        return True
    
    def __parseShortsKeys(self, shortKeys):
        index = 0
        indexedSet = list(shortKeys)
        while index < len(indexedSet):
            key = indexedSet[index]
            if key in self.shorts:
                del indexedSet[index]
                for item in self.shorts[key].params:
                    if not(item in indexedSet):
                        indexedSet.append(item)
                continue
            index += 1
        return set(indexedSet)

