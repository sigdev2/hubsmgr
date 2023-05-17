#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utility import archiveutils
from providers.providerproxy import ProviderProxy
from providers.archiveproxy import ArchiveProxy

class ManagedProxy(ProviderProxy):
    __slots__ = (r'__managed',)

    def __init__(self, source):
        self.__managed = {}
        super(ManagedProxy, self).__init__(source)

    def isPullSupport(self):
        for providers in self.__managed.values():
            for provider in providers:
                if provider.isPushSupport():
                    return True
        return False

    def isPushSupport(self):
        for providers in self.__managed.values():
            for provider in providers:
                if provider.isPullSupport():
                    return True
        return False

    def isCommitSupport(self):
        if self.source.isCommitSupport():
            return True
        for providers in self.__managed.values():
            for provider in providers:
                if provider.isCommitSupport():
                    return True
        return False

    def isCloneSupport(self):
        if self.source.isCloneSupport():
            return True
        for providers in self.__managed.values():
            for provider in providers:
                if provider.isCloneSupport():
                    return True
        return False

    def isValid(self):
        for providers in self.__managed.values():
            for provider in providers:
                if provider.isValid():
                    return True
        return False

    def isExist(self):
        if not self.source.isExist():
            return False
        for providers in self.__managed.values():
            for provider in providers:
                if not provider.isExist():
                    return False
        return True

    def addRemotes(self, remoteName, remotes):
        self.source.source.addRemotes(remoteName, remotes)
        if not remoteName in self.__managed:
            self.__managed[remoteName] = []
        baseProvider = self.source.source if isinstance(self.source, ProviderProxy) else self.source
        providerClass = type(baseProvider)
        for remote in remotes:
            provider = providerClass(remote, baseProvider.out)
            if archiveutils.isSupportedArchive(baseProvider.path):
                provider = ArchiveProxy(provider)
            self.__managed[remoteName].append(provider)
            provider.addRemotes(remoteName, [baseProvider.path])

    def commit(self, message, addAll):
        if self.source.isCommitSupport():
            e = self.source.commit(message, addAll)
            if e != 0:
                return e

        for providers in self.__managed.values():
            for provider in providers:
                if provider.isCommitSupport():
                    e = provider.commit(message, addAll)
                    if e != 0:
                        return e
        return 0

    def pull(self, remote, opts):
        if remote in self.__managed:
            for provider in self.__managed[remote]:
                if provider.isPushSupport():
                    e = provider.push(remote, opts)
                    if e != 0:
                        return e
        return 0

    def push(self, remote, opts):
        if remote in self.__managed:
            for provider in self.__managed[remote]:
                if provider.isPullSupport():
                    e = provider.pull(remote, opts)
                    if e != 0:
                        return e
        return 0

    def clone(self, remote, opts):
        if remote in self.__managed:
            if not self.source.isExist():
                if not self.source.isCloneSupport():
                    return -1

                hasRemote = False
                for provider in self.__managed[remote]:
                    if provider.isExist():
                        hasRemote = True
                        break

                if not hasRemote:
                    return -1

                e = self.source.clone(remote, opts)
                if e != 0:
                    return e

            for provider in self.__managed[remote]:
                if not provider.isExist() and provider.isCloneSupport():
                    e = provider.clone(remote, opts)
                    if e != 0:
                        return e
        return 0
