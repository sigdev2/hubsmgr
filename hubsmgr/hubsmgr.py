#!/usr/bin/env python
# -*- coding: utf-8 -*-

from operator import truediv
import os
import sys
import pathlib
import traceback
from utility.logger import Logger
from parsers.specyaml import SpecYamlParser
from parsers.shortsparser import ShortsParser
from parsers.projectsparser import ProjectsParser
from parsers.hubsparser import HubsParser
from providers.git import Git
from providers.pythonsync import PythonSync
from time import sleep

class UrlProperty:
    __slots__ = [r'remotes', r'opts']

    def __init__(self, remote, opts):
        self.remotes = set()
        self.remotes.add(remote)
        self.opts = opts
    
    def add(self, remote, opts):
        self.remotes.add(remote)
        self.opts = self.opts.union(opts)
        
class ProviderRoutes:
    __slots__ = [r'urls', r'paths']

    def __init__(self):
        self.urls = {}
        self.paths = {}
    
def syncOptions(projectOpts, hubOpts):
    hasSyncPull = r'pull' in projectOpts
    hasSyncPush = r'push' in projectOpts
    hasHubPull = r'pull' in hubOpts
    hasHubPush = r'push' in hubOpts

    isSyncPull = hasSyncPull or not(hasSyncPush)
    isSyncPush = hasSyncPush or not(hasSyncPull)
    isHubPull = hasHubPull or not(hasHubPush)
    isHubPush = hasHubPush or not(hasHubPull)

    return (isSyncPull and isHubPull, isSyncPush and isHubPush)

def createProvider( i, count, logTag,className, remote, projectName, projectPath, projectOpts, root, out):
    typeClass = globals()[className]
    provider = typeClass(remote, projectName, projectPath, root, (lambda message, isCommand : out(message)))
    Logger.partoperation(i, count, logTag, r'Create provider ' + remote + (r' ' + str(projectOpts) if len(projectOpts) > 0 else r'') + r' : ' + str(projectPath), True)
    provider.setOptions(projectOpts)
    return provider

def initProviders(i, count, logTag, providers, projectOpts):
    toPull = []
    toPush = []

    for provider, opts in providers:
        remoteName = provider.remoteName()

        Logger.partmessage(i, count, logTag, r'Provider hub ' + remoteName + r' (' + str(provider.url) + r')' + r' options: ' + str(opts))
        if not(provider.isExist()):
            ec = provider.clone()
            Logger.partoperation(i, count, logTag, r'Clone ' + remoteName + r' ' + str(provider.url) + r' -> ' + str(provider.path()), ec == 0)
            if ec != 0:
                Logger.error(r'Clone is return exit code: ' + str(ec))
                return False
        if r'freeze' in projectOpts:
            return (toPull, toPush)

        if r'freeze' in opts:
            continue

        if r'autocommit':
            ec = provider.commit(r'auto commit', True)
            Logger.partoperation(i, count, logTag, r'Auto commit from provider ' + remoteName + r' in ' + str(provider.path()), ec == 0)
            if ec != 0:
                Logger.error(r'Commit is return exit code: ' + str(ec))
                return False

        ec = provider.updateRemotes()
        Logger.partoperation(i, count, logTag, r'Update remotes for provider ' + remoteName + r' (' + str(provider.url) + r')', ec == 0)
        if ec != 0:
            Logger.error(r'Update remotes return exit code: ' + str(ec))
            return False
        
        isPull, isPush = syncOptions(projectOpts, opts)
        Logger.partmessage(i, count, logTag, r'Provider hub ' + remoteName + r' (' + str(provider.url) + r')' + r' operations :' + (r' pull' if isPull else r'') + (r' push' if isPush else r''))

        if isPull:
            toPull.append(provider)
        if isPush:
            toPush.append(provider)
    return (toPull, toPush)

def processProvider(className, logTag, i, count, paths, urls, root, project):
    projPath = root / project.name

    providers = []
    managedProviders = []

    out = (lambda message : Logger.partmessage(i, count, logTag, message))
    
    Logger.partmessage(i, count, logTag, r'Create project remote providers')
    for url in urls:
        for remote in urls[url].remotes:
            provider = createProvider(i, count, logTag, className, remote, project.name, url + project.name, project.opts, root, out)
            providers.append([provider, urls[url].opts])

    Logger.partmessage(i, count, logTag, r'Create project local providers')
    for path in paths:
        projectPath = path + project.name
        hostPath = pathlib.Path(projectPath)
        if (projPath == hostPath) or (root == hostPath) or \
           (hostPath.is_relative_to(root)) or (hostPath.is_relative_to(projPath)) or \
           (projPath.is_relative_to(hostPath)):
           continue
        for remote in paths[path].remotes:
            if r'managed' in paths[path].opts:
                remoteProvider = createProvider(i, count, logTag, className, r'origin', project.name, hostPath, project.opts, hostPath.parent, out)
                managedProviders.append((remoteProvider, paths[path].opts))
            else:
                provider = createProvider(i, count, logTag, className, remote, project.name, projectPath, project.opts, root, out)
                providers.append((provider, paths[path].opts))

    Logger.partmessage(i, count, logTag, r'Init providers')
    result = initProviders(i, count, logTag, providers, project.opts)
    if result == False:
        return
    toPull, toPush = result
    
    Logger.partmessage(i, count, logTag, r'Init managed providers')
    result = initProviders(i, count, logTag, managedProviders, project.opts)
    if result == False:
        return
    managedToPull, managedToPush  = result

    if (len(toPull) + len(toPush) + len(managedToPull) + len(managedToPush)) == 0:
        return

    Logger.partmessage(i, count, logTag, r'Sync providers')

    for provider in toPull:
        ec = provider.pull()
        Logger.partoperation(i, count, logTag, r'<- Pull from ' + provider.remoteName() + r' (' + str(provider.url) + r')', ec == 0)
        if ec != 0:
            Logger.error(r'Pull is return exit code: ' + str(ec))
            return
    
    for provider in managedToPush:
        ec = provider.push()
        Logger.partoperation(i, count, logTag, r'<- Push from managed ' + provider.remoteName() + r' (' + str(provider.url) + r')', ec == 0)
        if ec != 0:
            Logger.error(r'Push managed repository is return exit code: ' + str(ec))
            return

    for provider in toPush:
        ec = provider.push()
        Logger.partoperation(i, count, logTag, r'-> Push to ' + provider.remoteName() + r' (' + str(provider.url) + r')', ec == 0)
        if ec != 0:
            Logger.error(r'Push is return exit code: ' + str(ec))
            return
    
    for provider in managedToPull:
        ec = provider.pull()
        Logger.partoperation(i, count, logTag, r'-> Pull to managed ' + provider.remoteName() + r' (' + str(provider.url) + r')', ec == 0)
        if ec != 0:
            Logger.error(r'Pull managed repository is return exit code: ' + str(ec))
            return

def mergeProjectHubs(hubs):
    providers = {}
    for hub in hubs:
        if not(hub.provider in providers):
            providers[hub.provider] = ProviderRoutes()
        provider = providers[hub.provider]

        for url in hub.urls:
            if url in provider.urls:
                provider.urls[url].add(hub.id, hub.opts)
            else:
                provider.urls[url] = UrlProperty(hub.id, hub.opts)
        
        for path in hub.paths:
            if path in provider.paths:
                provider.paths[path].add(hub.id, hub.opts)
            else:
                provider.paths[path] = UrlProperty(hub.id, hub.opts)
    return providers

def processProjects(projects, root):
    i = 0
    count = len(projects)
    for project in projects:
        Logger.partstart(i, count, project + r': ' + r' '.join(projects[project].syncParams))

        providers = mergeProjectHubs(projects[project].hubs)
        for provider in providers:
            if provider == r'git':
                processProvider(r'Git', r'GIT', i, count, providers[provider].paths, providers[provider].urls, root, projects[project])
            elif provider == r'pysync':
                processProvider(r'PythonSync', r'PYSYNC', i, count, providers[provider].paths, providers[provider].urls, root, projects[project])

        i += 1
        Logger.partend(i, count, project)

def sync(config):
    os.chdir(config.parent)
    rootPath = config.parent / config.stem
    if not(rootPath.exists()) or not(rootPath.is_dir()):
        rootPath.mkdir()
        Logger.operation(r'FS', r'Make root folder: ' + ascii(rootPath.as_posix()), rootPath.exists())
    if not(rootPath.exists()):
        Logger.error(r'Root folder is not exist')
        return

    Logger.message(r'YAML', r'Load yaml: ' + ascii(config.as_posix()))

    shortsParser = ShortsParser()
    hubsParser = HubsParser()
    projectsParser = ProjectsParser(shortsParser.shorts, hubsParser.hubs)

    with config.open(r'r') as f:
        parser = SpecYamlParser(f)
        parser.addParser(shortsParser)
        parser.addParser(hubsParser)
        parser.addParser(projectsParser)
        parser.parse()
    
    Logger.message(r'YAML', r'Finded shorts [' + str(len(shortsParser.shorts)) + r']')
    Logger.message(r'YAML', r'Finded hubs [' + str(len(hubsParser.hubs)) + r']')
    Logger.message(r'YAML', r'Finded projects [' + str(len(projectsParser.projects)) + r']')

    Logger.headerStart(r'SYNC', ascii(rootPath.as_posix()))
    processProjects(projectsParser.projects, rootPath)
    Logger.headerEnd(r'SYNC')

if __name__ == r'__main__':
    try:
        if (len(sys.argv)) < 2 or (len(sys.argv[1]) <= 0):
            Logger.error(r'No input yaml file or directory')
        
        path = pathlib.Path(os.path.abspath(sys.argv[1].strip()))

        if path.is_dir():
            path = path.resolve()
            Logger.message(r'FS', r'Load yamls from ' + ascii(path.as_posix()))
            for ext in (r'*.yaml', r'*.yml'):
                for filename in path.glob(ext):
                    sync(filename)
        else:
            if path.is_file():
                sync(path)
            else:
                Logger.error(r'Input yaml file is not exists "' + ascii(path.as_posix()) + r'"')
    except Exception as e:
        print(traceback.format_exc())
        sleep(20)