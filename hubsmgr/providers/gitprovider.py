#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from provider import Provider

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), r'../')))

from gitutils import git, gitoptions
from utility import pathutils

class GitProvider(Provider):
    __slots__ = (r'path', r'out', r'git', r'__remotes')

    def __init__(self, path, out = None):
        self.__remotes = dict()
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
        if not(remoteName in self.__remotes):
            self.__remotes[remoteName] = set()
        for remote in remotes:
            self.__remotes[remoteName].add(remote)

    def commit(self, message, addAll):
        if not(self.git.hasChanges()):
            return 0
        return self.git.commit(message, addAll)

    def pull(self, remote, opts):
        for url in self.__remotes:
            self.git.addRemote(remote, url)
            opts = gitoptions.GitOptions(remote, opts, self.git)

            # store revision with context
            storedRevision = r''
            storedBranch = r''
            storedIsBranchHead = False
            def storeRevision():
                storedBranch = self.git.getCurrentBranch()
                storedRevision = self.git.getRevision(r'HEAD')
                storedIsBranchHead = (storedRevision == self.git.getRevision(storedBranch))
                return r''
            cmds = [storeRevision]

            # fetch and merge branches
            for branch, isNew in opts.getBranchesToPull().items():
                cmds += self.git.pull_branch_with_checkout(remote, branch, isNew, opts.unrelated, True)

            # fetch tags
            if not(opts.notags):
                for tag in opts.getTagsToPull():
                    cmds += self.git.pull_tag(remote, tag, True)

            # store free tags
            storedFreeTags = set()
            if not(opts.notags):
                def storeFreeTags():
                    storedFreeTags = opts.getAllFreeTags()
                    return r''
                cmds.append(storeFreeTags)

            # restore revision
            def restoreRevision():
                newRevision = self.git.getRevision(r'HEAD')

                # restore strict specified revision
                if len(opts.revisions) > 0:
                    checkoutRevision = storedRevision
                    if len(storedRevision) <= 0 or not(storedRevision in opts.revisions):
                        checkoutRevision = list(opts.revisions)[0]
                    if newRevision != checkoutRevision:
                        return self.git.checkout(remote, checkoutRevision, True)
                    return r''

                # restore strict specified tag
                if not(opts.notags):
                    strictTags = opts.tags.difference(storedFreeTags)
                    if len(strictTags) > 0:
                        checkoutRevision = None
                        checkoutTag = list(strictTags)[0]
                        for tag, revision in opts.getRealTagsRevisions(strictTags).items():
                            if revision == storedRevision:
                                checkoutTag = tag
                                checkoutRevision = revision
                                break
                        if (checkoutRevision == None) or (newRevision != checkoutRevision):
                            return self.git.checkout(remote, checkoutTag, True)
                        return r''

                # restore HEAD strict specified branch
                if len(opts.branches) > 0:
                    checkoutBranch = storedBranch if storedBranch in opts.branches else list(opts.branches)[0]
                    checkoutRevision = opts.getRealBranchRevision(checkoutBranch)
                    if (checkoutRevision == None) or (newRevision != checkoutRevision):
                        return self.git.checkout(remote, branch, True)
                    return r''

                # restore last revision
                if newRevision != storedRevision:
                    if len(storedBranch) > 0 and storedIsBranchHead:
                        return self.git.checkout(remote, storedBranch, True)
                    return self.git.checkout(remote, storedRevision, True)
                return r''
            cmds.append(restoreRevision)

            # checkout free tags
            if not(opts.notags):
                for tag in storedFreeTags.intersection(opts.tags):
                    cmds += self.git.checkout(remote, tag + r' .', True)

            # update submodules
            if not(opts.nosubmodules):
                cmds += self.git.updateSubmodules(True)

            e = self.git.run(cmds, self.out)
            if e != 0:
                return e
        return 0

    def push(self, remote, opts):
        for url in self.__remotes:
            self.git.addRemote(remote, url)
            opts = gitoptions.GitOptions(remote, opts, self.git)

            cmds = []

            pushBranches = opts.getBranchesToPush()
            for branch in pushBranches:
                cmds += self.git.push(remote, branch, True)

            if not(opts.notags):
                pushTags = opts.getTagsToPush()
                for tag in pushTags:
                    cmds += self.git.push(remote, tag, True)

            if len(cmds) > 0:
                e = self.git.run(cmds, self.out)
                if e != 0:
                    return e
        return 0

    def clone(self, remote, opts):
        for url in self.__remotes:
            self.git.addRemote(remote, url)
            opts = gitoptions.GitOptions(remote, opts, self.git)
            e = self.git.clone(remote, self.path, opts.bare)
            if e == 0:
                return 0
        return -1
