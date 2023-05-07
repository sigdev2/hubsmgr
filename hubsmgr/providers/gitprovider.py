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
        pass
    
    def commit(self, message, addAll):
        if not(self.git.hasChanges()):
            return 0
        return self.git.commit(message, addAll)

    def pull(self, remote, opts):
        return -1
    
    def push(self, remote, opts):
        return -1
    
    def clone(self, remote, opts):
        return -1

    def commit(self, message, addAll):
        self.__updateChanges()
        self.__updateBranchesAndTags()
        
        if not(self.opts.canCommit()):
            return 0

        cmds = []
        if addAll:
            cmds.append(r'git add -A')
        cmds.append(r'git commit -m "' + message + r'"')
        return self.run(cmds, self.out, self.path())

    def pull(self):
        self.__updateBranchesAndTags()

        cmds = []

        pullBranches = self.opts.branchesToPull()
        for branch, isNew in pullBranches.items():
            cmds.append(r'git fetch ' + self.opts.remoteName + r' ' + branch + (r':' + branch if isNew else r''))
            if not(isNew):
                cmds.append(lambda : r'git checkout ' + branch if self.__getCurrentBranch() != branch else r'')
                cmds.append(r'git merge ' + (r'--allow-unrelated-histories ' if self.opts.unrelated else r'') + self.opts.remoteName + r'/' + branch)
        
        if not(self.opts.notags):
            for tag in self.opts.tagsToPull():
                cmds.append(r'git fetch ' + self.opts.remoteName + r' ' + tag)
        
        cmds.append(self.__checkoutCommands())

        return self.run(cmds, self.out, self.path())

    def push(self):
        self.__updateBranchesAndTags()

        cmds = []

        pushBranches = self.opts.branchesToPush()
        for branch in pushBranches:
            cmds.append(r'git push ' + self.opts.remoteName + r' ' + branch + r':' + branch)

        if not(self.opts.notags):
            pushTags = self.opts.tagsToPush()
            for tag in pushTags:
                cmds.append(r'git push ' + self.opts.remoteName + r' ' + tag + r':' + tag)
        
        if len(cmds) <= 0:
            return 0

        return self.run(cmds, self.out, self.path())
        
    def clone(self):
        opts = r' -o ' + self.remoteName()
        opts += r' ' + str(self.url)
        opts += r' .' + os.sep + self.name + os.sep

        return self.run(r'git clone' + opts, self.out, self.root)