#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pathlib
import traceback
from time import sleep

import utility.utils
from utility.logger import Logger
from process import ProjectProcessor

def processProjects(projects, root):
    i = 0
    count = len(projects)
    processor = ProjectProcessor(root, count, Logger)
    for project in projects:
        processor.process(project, i)
        i += 1

def sync(config):
    os.chdir(config.parent)
    rootPath = utility.utils.configdir(config)
    if not(rootPath):
        Logger.error(r'Root folder for ' + ascii(config.as_posix())) + r' is not exist'
        return

    Logger.message(r'YAML', r'Parse yaml: ' + ascii(config.as_posix()))
    projectsParser = utility.utils.parseconfig(config)
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
            for file in utility.utils.yamlpaths(path):
                sync(file)
    except Exception as e:
        print(traceback.format_exc())
        sleep(20)