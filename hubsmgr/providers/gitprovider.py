#!/usr/bin/env python
# -*- coding: utf-8 -*-

from providers.provider import Provider
from gitutils import git, gitoptions
from utility import pathutils

class GitProvider(Provider):
    __slots__ = [r'path', r'out', r'git']

    def __init__(self, path, out = None):
        self.git = git.Git(path, self.run, out)
        super(GitProvider, self).__init__(path, out)
    
    def isPullSupport(self):
        return True
    
    def isPushSupport(self):
        return True
    
    def isCommitSupport(self):
        currentBranch = self.git.getCurrentBranch()
        return len(currentBranch) > 0 and self.git.getRevision(currentBranch) == self.git.getRevision(r'HEAD')
    
    def isCloneSupport(self):
        return True
    
    def isValid(self):
        return not(pathutils.isUrl(self.path))
    
    def isExist(self):
        return self.git.isRepository(False) or self.git.isRepository(True)
    
    def addRemotes(self, remoteName, remotes):
        self.git.addRemote(remoteName)
    
    def commit(self, message, addAll):
        if not(self.git.hasChanges()):
            return 0
        return self.git.commit(message, addAll)

    def pull(self, remote, opts):
        opts = gitoptions.GitOptions(remote, opts, self.git)

        cmds = []

        for branch, isNew in opts.getBranchesToPull().items():
            cmds += self.git.pull_branch_with_checkout(remote, branch, isNew, opts.unrelated, True)
        
        if not(opts.notags):
            for tag in opts.getTagsToPull():
                cmds += self.git.pull_tag(remote, tag, True)
        
        cmds.append(self.__checkoutCommands())

        
        if not(opts.nosubmodules):
            cmds += self.git.updateSubmodules(True)

        return self.git.run(cmds)
    
    def push(self, remote, opts):
        opts = gitoptions.GitOptions(remote, opts, self.git)

        cmds = []

        pushBranches = opts.getBranchesToPush()
        for branch in pushBranches:
            cmds += self.git.push(remote, branch, True)

        if not(opts.notags):
            pushTags = opts.tagsToPush()
            for tag in pushTags:
                cmds += self.git.push(remote, tag, True)
        
        if len(cmds) <= 0:
            return 0

        return self.git.run(cmds)
    
    def clone(self, remote, opts):
        opts = gitoptions.GitOptions(remote, opts, self.git)
        return self.git.clone(remote, self.path, opts.bare)