#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utility import pathutils, archiveutils, synccommands
from providers.gitprovider import GitProvider
from providers.pythonsync import PythonSync
from providers.archiveproxy import ArchiveProxy
from providers.managedproxy import ManagedProxy

def getPulPushOptions(opts):
    hasPull = r'pull' in opts
    hasPush = r'push' in opts
    return (hasPull or not hasPush), (hasPush or not hasPull)

class ProjectProcessor:
    __slots__ = (r'__root', r'__out')

    SYNC_COMMANDS = synccommands.SyncCommands([lambda pair, opts: \
                                  pair[1].clone(pair[0], opts) if not(pair[1].isExist()) else None,
                                  lambda pair, opts: pair[1].commit(r'auto commit', True),
                                  lambda pair, opts: pair[1].pull(pair[0], opts),
                                  lambda pair, opts: pair[1].push(pair[0], opts)]) # todo: add logs comments of operations

    def __init__(self, root, out):
        self.__root = root
        self.__out = out

    def process(self, project):
        sync = project.parameters[r'sync']
        isFreeze = r'freeze' in sync
        isAutocommit = r'autocommit' in sync
        isPull, isPush = getPulPushOptions(sync)

        # todo: unpak project parameners like zip pass or local zip init
        projectPath = self.__root / project.id
        hubs = project.parameters[r'hubs']

        self.__out(project.id + r' :' + \
                   (r' autocommit' if isAutocommit else r'') + \
                   (r' pull' if isPull else r'') + \
                   (r' push' if isPush else r''), r'OPTS')

        self.__out(project.id + r' : ' + r''.join([hub.id for hub in hubs]), r'HUBS')

        for hub in hubs:
            opts = hub.parameters[r'options']
            paths = pathutils.unpackSyncPaths(hub.parameters[r'paths'], project.id, self.__root)
            isHubPull, isHubPush = getPulPushOptions(opts)
            provider = self.__createProvider(next(iter(hub.parameters[r'providers'])),
                                             projectPath, hub.id, paths, r'managed' in opts)
            if provider is not None:
                command = ProjectProcessor.SYNC_COMMANDS.create(
                    (True, isAutocommit, isPull, isPush),
                    (hub.id, provider))
                command.merge((provider.isCloneSupport(), provider.isCommitSupport(),
                               provider.isPullSupport(), provider.isPushSupport()))
                command.merge((True, not isFreeze, isHubPull and not isFreeze,
                               isHubPush and not isFreeze))
                ProjectProcessor.SYNC_COMMANDS.add(command)

        ProjectProcessor.SYNC_COMMANDS.exec((project.parameters[r'options'],))

    def __createProvider(self, name, path, remoteName, remotes, managed):
        provider = None
        if name == r'pysync':
            provider = PythonSync(path, lambda m, _: self.__out(m, r'PYSYNC'))
        elif name == r'git':
            provider = GitProvider(path, lambda m, _: self.__out(m, r'GIT'))
        if provider is not None:
            if archiveutils.isSupportedArchive(path):
                provider = ArchiveProxy(provider)
            if managed:
                provider = ManagedProxy(provider)
            provider.addRemotes(remoteName, remotes)
            if provider.isValid():
                return provider
        return None
