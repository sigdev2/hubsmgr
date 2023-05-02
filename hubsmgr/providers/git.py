#!/usr/bin/env python
# -*- coding: utf-8 -*-

from providers.provider import Provider
import os
import re

GIT_SIGN = r'.git'

class Git(Provider):
    def __init__(self, hub, name, url, root, out = None):
        super(Git, self).__init__(hub, name, url, root, out)

    def isExist(self):
        gitSignPath = self.path() / GIT_SIGN
        return Provider.isExist(self) and gitSignPath.exists() and gitSignPath.is_dir()
    
    def updateRemotes(self):
        remoteName = self.remoteName()
        if not(self.__hasRemote(remoteName)):
            ec = self.run(r'git remote add ' + remoteName + r' ' + str(self.url), self.out, self.path())
            if ec != 0:
                return ec
        elif self.__getRemoteUrl(remoteName) != str(self.url):
            ec = self.run(r'git remote set-url ' + remoteName + r' ' + str(self.url), self.out, self.path())
            if ec != 0:
                return ec
        
        return 0

    def setOptions(self, val):
        self.opts = GitOptions()

        self.opts.remoteName = self.remoteName()

        for opt in val:
            if is_sha1(opt):
                self.opts.revisions.add(opt)
            elif opt == r'notags':
                self.opts.notags = True
            elif opt == r'nosub':
                self.opts.nosubmodules = True
            elif opt == r'unrelated':
                self.opts.unrelated = True
            else:
                self.opts.arguments.add(opt)

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