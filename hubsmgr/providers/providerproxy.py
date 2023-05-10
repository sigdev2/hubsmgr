#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ProviderProxy:
    __slots__ = (r'source')

    def __init__(self, source):
        self.source = source
    
    def isPullSupport(self):
        return self.source.isPullSupport()
    
    def isPushSupport(self):
        return self.source.isPushSupport()
    
    def isCommitSupport(self):
        return self.source.isCommitSupport()
    
    def isCloneSupport(self):
        return self.source.isCloneSupport()
    
    def isValid(self):
        return self.source.isValid()
    
    def isExist(self):
        return self.source.isExist()
    
    def addRemotes(self, remoteName, remotes):
        self.source.addRemotes(remoteName, remotes)
    
    def commit(self, message, addAll):
        return self.source.commit(message, addAll)

    def pull(self, remote, opts):
        return self.source.pull(remote, opts)
    
    def push(self, remote, opts):
        return self.source.push(remote, opts)
    
    def clone(self, remote, opts):
        return self.source.clone(remote, opts)