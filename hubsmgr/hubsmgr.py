#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pathlib
import traceback
from time import sleep

from utility import pathutils
from utility.logger import Logger
from process import ProjectProcessor
from parsers.shortsparser import SpecYamlParser

def processProjects(projects, root):
    i = 0
    logTag = r''
    def out(message, isCommand):
        Logger.partmessage(i, len(projects), logTag, message)
    processor = ProjectProcessor(root, out)
    for name, project in projects.items():
        processor.process(name, project)
        i += 1

def sync(config):
    os.chdir(config.parent)
    rootPath = pathutils.configdir(config)
    if not rootPath:
        Logger.error(r'Root folder for ' + ascii(config.as_posix()) + r' is not exist')
        return

    Logger.message(r'YAML', r'Parse yaml: ' + ascii(config.as_posix()))
    projectsParser = SpecYamlParser.parseconfig(config)
    Logger.message(r'YAML', r'Finded hubs [' + str(len(projectsParser.hubs)) + r']')
    Logger.message(r'YAML', r'Finded projects [' + str(len(projectsParser.projects)) + r']')

    Logger.headerStart(r'SYNC', ascii(rootPath.as_posix()))
    processProjects(projectsParser.projects, rootPath)
    Logger.headerEnd(r'SYNC')

if __name__ == r'__main__':
    try:
        if (len(sys.argv)) < 2 or (len(sys.argv[1]) <= 0):
            Logger.error(r'No input yaml file or directory')
        else:
            path = pathlib.Path(os.path.abspath(sys.argv[1].strip()))
            for file in pathutils.yamlpaths(path):
                sync(file)
    except Exception as e:
        print(traceback.format_exc())
        sleep(20)
