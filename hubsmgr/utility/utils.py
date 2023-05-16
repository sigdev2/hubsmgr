#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parsers.specyaml import SpecYamlParser
from parsers.shortsparser import ShortsParser
from parsers.projectsparser import ProjectsParser
from parsers.hubsparser import HubsParser

def parseconfig(config):
    shortsParser = ShortsParser()
    hubsParser = HubsParser()
    projectsParser = ProjectsParser(shortsParser.shorts, hubsParser.hubs)
    with config.open(r'r') as f:
        SpecYamlParser().parse([shortsParser, hubsParser, projectsParser], f)
    return projectsParser
