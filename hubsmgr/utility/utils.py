#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parsers.specyaml import SpecYamlParser
from parsers.shortsparser import ShortsParser
from parsers.projectsparser import ProjectsParser
from parsers.hubsparser import HubsParser

def yamlpaths(path):
    paths = []
    if path.is_dir():
        path = path.resolve()
        paths = [f for ext in (r'*.yaml', r'*.yml') for f in path.glob(ext)]
    elif path.is_file():
        paths.append(path)
    return paths

def configdir(config):
    rootPath = config.parent / config.stem
    if not(rootPath.exists()) or not(rootPath.is_dir()):
        rootPath.mkdir()
    if not(rootPath.exists()):
        return False
    return rootPath

def parseconfig(config):
    shortsParser = ShortsParser()
    hubsParser = HubsParser()
    projectsParser = ProjectsParser(shortsParser.shorts, hubsParser.hubs)
    with config.open(r'r') as f:
        SpecYamlParser().parse([shortsParser, hubsParser, projectsParser], f)
    return projectsParser