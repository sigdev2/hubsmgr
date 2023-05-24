#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utility import pathutils, archiveutils, syncutils
from providers.gitprovider import GitProvider
from providers.pythonsync import PythonSync
from providers.archiveproxy import ArchiveProxy
from providers.managedproxy import ManagedProxy

class ProjectProcessor:
    __slots__ = (r'__root', r'__out')

    def __init__(self, root, out):
        self.__root = root
        self.__out = out

    def process(self, project):
        sync = project.parameters[r'sync']
        isFreeze = r'freeze' in sync
        isAutocommit = r'autocommit' in sync
        isPull, isPush = syncutils.getPulPushOptions(sync)

        projectPath = self.__root / project.parameters[r'target']
        projectPath = projectPath.resolve()

        hubs = project.parameters[r'hubs']
        auth = project.parameters[r'auth']

        self.__out(project.id + r' :' + \
                   (r' autocommit' if isAutocommit else r'') + \
                   (r' pull' if isPull else r'') + \
                   (r' push' if isPush else r''), r'OPTS')

        self.__out(project.id + r' : ' + r''.join([hub.id for hub in hubs]), r'HUBS')

        for hub in hubs:
            opts = hub.parameters[r'options']
            paths = pathutils.unpackSyncPaths(hub.parameters[r'paths'], project.id, self.__root)
            isHubPull, isHubPush = syncutils.getPulPushOptions(opts)
            provider = self.__createProvider(next(iter(hub.parameters[r'providers'])),
                                             projectPath, hub.id, paths, r'managed' in opts,
                                             auth)
            if provider is not None:
                command = syncutils.PROVIDER_CMDS.create(
                    (True, isAutocommit, isPull, isPush),
                    syncutils.SyncUnit(hub.id, provider))
                command.merge((provider.isCloneSupport(), provider.isCommitSupport(),
                               provider.isPullSupport(), provider.isPushSupport()))
                command.merge((True, not isFreeze, isHubPull and not isFreeze,
                               isHubPush and not isFreeze))
                syncutils.PROVIDER_CMDS.add(command)

        return syncutils.PROVIDER_CMDS.exec((project.parameters[r'options'],))

    def __createProvider(self, name, path, remoteName, remotes, managed, auth):
        provider = None
        if name == r'pysync':
            provider = PythonSync(path, lambda m, _: self.__out(m, r'PYSYNC'))
        elif name == r'git':
            provider = GitProvider(path, lambda m, _: self.__out(m, r'GIT'))
        if provider is not None:
            if archiveutils.isSupportedArchive(path):
                self.__out(r'Is archived provider for remote ' + remoteName, r'ARCHIVED')
                #todo: use auth for archive
                provider = ArchiveProxy(provider)
            if managed:
                self.__out(r'Is managed provider for remote ' + remoteName, r'MANAGED')
                provider = ManagedProxy(provider)
            self.__out(r'Add remote urls from ' + remoteName + r' : ' + str(remotes), r'URLS')
            provider.addRemotes(remoteName, remotes)
            if provider.isValid():
                return provider
        return None
