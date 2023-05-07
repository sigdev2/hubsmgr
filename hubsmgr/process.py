#!/usr/bin/env python
# -*- coding: utf-8 -*-

import utility.pathutils
import utility.archiveutils
from synccommands import SyncCommands
from providers.gitprovider import GitProvider
from providers.pythonsync import PythonSync
from providers.archiveproxy import ArchiveProxy
from providers.managedproxy import ManagedProxy

def getPulPushOptions(opts):
    hasPull = r'pull' in opts
    hasPush = r'push' in opts
    return (hasPull or not(hasPush)), (hasPush or not(hasPull))

class ProjectProcessor:
    __slots__ = [r'__root', r'__out']

    SYNC_COMMANDS = SyncCommands([lambda pair, opts: pair[1].clone(pair[0], opts) if not(pair[1].isExist()) else None,
                                  lambda pair, opts: pair[1].commit(r'auto commit', True),
                                  lambda pair, opts: pair[1].pull(pair[0], opts),
                                  lambda pair, opts: pair[1].push(pair[0], opts)])

    def __init__(self, root, out):
        self.__root = root
        self.__out = out

    def process(self, name, project):
        sync = project.parameters[r'sync']
        isFreeze = r'freeze' in sync
        isAutocommit = r'autocommit' in sync
        isPull, isPush = getPulPushOptions(sync)

        projectPath = self.__root / name
        
        for remoteName, hub in project.parameters[r'hubs'].items():
            opts = hub.parameters[r'options']
            paths = utility.pathutils.unpackSyncPaths(hub.parameters[r'paths'], name, self.__root)
            isHubPull, isHubPush = getPulPushOptions(opts)
            provider = self.__createProvider(hub.parameters[r'providers'][0], projectPath, remoteName, paths, r'managed' in opts)
            if provider != None:
                command = ProjectProcessor.SYNC_COMMANDS.create((True, isAutocommit, isPull, isPush), (remoteName, provider))
                command.merge((provider.isCloneSupport(), provider.isCommitSupport(), provider.isPullSupport(), provider.isPushSupport()))
                command.merge((True, not(isFreeze), isHubPull and not(isFreeze), isHubPush and not(isFreeze)))
                ProjectProcessor.SYNC_COMMANDS.add(command)

        ProjectProcessor.SYNC_COMMANDS.exec((project.parameters[r'options']))

    def __createProvider(self, name, path, remoteName, remotes, managed):
        provider = None
        if name == r'pysync':
            provider = PythonSync(path, self.__out)
        elif name == r'git':
            provider = GitProvider(path, self.__out)
        if provider != None:
            if utility.archiveutils.isSupportedArchive(path):
                provider = ArchiveProxy(provider)
            if managed:
                provider = ManagedProxy(provider)
            provider.addRemotes(remoteName, remotes)
            if provider.isValid():
                return provider
        return None