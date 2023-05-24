#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utility import archiveutils
from providers.providerproxy import ProviderProxy
from providers.archiveproxy import ArchiveProxy

class ManagedProxy(ProviderProxy):
    __slots__ = (r'__managed',)

    def __init__(self, source):
        self.__managed = {}
        super().__init__(source)

    def __getattr__(self, name):
        if name in ManagedProxy.__slots__:
            return object.__getattribute__(self, name)
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name in ManagedProxy.__slots__:
            return object.__setattr__(self, name, value)
        return super().__setattr__(name, value)

    def isPullSupport(self):
        for providers in self.__managed.values():
            for provider in providers:
                if provider.isValid() and provider.isPushSupport():
                    return True
        return False

    def isPushSupport(self):
        for providers in self.__managed.values():
            for provider in providers:
                if provider.isValid() and provider.isPullSupport():
                    return True
        return False

    def isCommitSupport(self):
        if self.source.isValid() and self.source.isCommitSupport():
            return True
        for providers in self.__managed.values():
            for provider in providers:
                if provider.isValid() and provider.isCommitSupport():
                    return True
        return False

    def isCloneSupport(self):
        if self.source.isValid() and self.source.isCloneSupport():
            return True
        for providers in self.__managed.values():
            for provider in providers:
                if provider.isValid() and provider.isCloneSupport():
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
        ProviderProxy.addRemotes(self, remoteName, remotes)
        if not remoteName in self.__managed:
            self.__managed[remoteName] = []
        providerClass = self.baseType()
        for remote in remotes:
            provider = providerClass(remote, self.out)
            if archiveutils.isSupportedArchive(remote):
                #todo: auth for archives
                provider = ArchiveProxy(provider)
            self.__managed[remoteName].append(provider)
            provider.addRemotes(remoteName, { self.path })

    def commit(self, message, addAll):
        if self.source.isValid() and self.source.isCommitSupport():
            e = self.source.commit(message, addAll)
            if e != 0:
                return e

        for providers in self.__managed.values():
            for provider in providers:
                if provider.isValid() and provider.isCommitSupport():
                    e = provider.commit(message, addAll)
                    if e != 0:
                        return e
        return 0

    def pull(self, remote, opts):
        if remote in self.__managed:
            for provider in self.__managed[remote]:
                if provider.isValid() and provider.isPushSupport():
                    e = provider.push(remote, opts)
                    if e != 0:
                        return e
        return 0

    def push(self, remote, opts):
        if remote in self.__managed:
            for provider in self.__managed[remote]:
                if provider.isValid() and provider.isPullSupport():
                    e = provider.pull(remote, opts)
                    if e != 0:
                        return e
        return 0

    def clone(self, remote, opts):
        if remote in self.__managed:
            if not self.source.isExist():
                if not self.source.isValid() or not self.source.isCloneSupport():
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
                if not provider.isExist() and provider.isValid() and provider.isCloneSupport():
                    e = provider.clone(remote, opts)
                    if e != 0:
                        return e
        return 0
