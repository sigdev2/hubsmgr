#!/usr/bin/env python
# -*- coding: utf-8 -*-

from providers.provider import Provider
from gitutils import git, gitoptions
from utility import pathutils

class CheckoutContext:
    __slots__ = (r'revision', r'branch', r'isBranchHead', r'freeTags')

    def __init__(self):
        self.revision = r''
        self.branch = r''
        self.isBranchHead = False
        self.freeTags = set()

class GitProvider(Provider):
    __slots__ = (r'__git',)

    def __init__(self, path, out = None):
        self.__git = git.Git(path, self.run, out)
        super(GitProvider, self).__init__(path, out)

    def isPullSupport(self):
        return True

    def isPushSupport(self):
        return True

    def isCommitSupport(self):
        currentBranch = self.__git.getCurrentBranch()
        return len(currentBranch) > 0 and \
               self.__git.getRevision(currentBranch) == self.__git.getRevision(r'HEAD')

    def isCloneSupport(self):
        return True

    def isValid(self):
        return not pathutils.isUrl(self.path)

    def isExist(self):
        return self.__git.isRepository(False) or self.__git.isRepository(True)

    def commit(self, message, addAll):
        if not self.__git.hasChanges():
            return 0
        return self.__git.commit(message, addAll)

    def pull(self, remote, opts):
        storedContext = CheckoutContext()
        for url in self.remotes:
            self.__git.addRemote(remote, url)
            opts = gitoptions.GitOptions(remote, opts, self.__git)

            # store revision with context
            def storeRevision():
                storedContext.revision = self.__git.getRevision(r'HEAD')
                storedContext.branch = self.__git.getCurrentBranch()
                storedContext.isBranchHead = \
                    storedContext.revision == self.__git.getRevision(storedContext.branch)
                return r''
            cmds = [storeRevision]

            # fetch and merge branches
            for branch, isNew in opts.getBranchesToPull().items():
                cmds += self.__git.pull_branch_with_checkout(remote, branch,
                                                             isNew, opts.unrelated, True)

            # fetch tags
            if not opts.notags:
                for tag in opts.getTagsToPull():
                    cmds += self.__git.pull_tag(remote, tag, True)

            # store free tags
            if not opts.notags:
                def storeFreeTags():
                    storedContext.freeTags = opts.getAllFreeTags()
                    return r''
                cmds.append(storeFreeTags)

            # restore revision
            def restoreRevision():
                newRevision = self.__git.getRevision(r'HEAD')

                # restore strict specified revision
                if len(opts.revisions) > 0:
                    checkoutRevision = storedContext.revision
                    if len(storedContext.revision) <= 0 or \
                       not storedContext.revision in opts.revisions:
                        checkoutRevision = list(opts.revisions)[0]
                    if newRevision != checkoutRevision:
                        return self.__git.checkout(remote, checkoutRevision, True)
                    return r''

                # restore strict specified tag
                if not opts.notags:
                    strictTags = opts.tags.difference(storedContext.freeTags)
                    if len(strictTags) > 0:
                        checkoutRevision = None
                        checkoutTag = list(strictTags)[0]
                        for tag, revision in opts.getRealTagsRevisions(strictTags).items():
                            if revision == storedContext.revision:
                                checkoutTag = tag
                                checkoutRevision = revision
                                break
                        if (checkoutRevision is None) or (newRevision != checkoutRevision):
                            return self.__git.checkout(remote, checkoutTag, True)
                        return r''

                # restore HEAD strict specified branch
                if len(opts.branches) > 0:
                    checkoutBranch = storedContext.branch \
                                     if storedContext.branch in opts.branches \
                                     else list(opts.branches)[0]
                    checkoutRevision = opts.getRealBranchRevision(checkoutBranch)
                    if (checkoutRevision is None) or (newRevision != checkoutRevision):
                        return self.__git.checkout(remote, branch, True)
                    return r''

                # restore last revision
                if newRevision != storedContext.revision:
                    if len(storedContext.branch) > 0 and storedContext.isBranchHead:
                        return self.__git.checkout(remote, storedContext.branch, True)
                    return self.__git.checkout(remote, storedContext.revision, True)
                return r''
            cmds.append(restoreRevision)

            # checkout free tags
            if not opts.notags:
                for tag in storedContext.freeTags.intersection(opts.tags):
                    cmds += self.__git.checkout(remote, tag + r' .', True)

            # update submodules
            if not opts.nosubmodules:
                cmds += self.__git.updateSubmodules(True)

            e = self.__git.run(cmds, self.out)
            if e != 0:
                return e
        return 0

    def push(self, remote, opts):
        for url in self.remotes:
            self.__git.addRemote(remote, url)
            opts = gitoptions.GitOptions(remote, opts, self.__git)

            cmds = []

            pushBranches = opts.getBranchesToPush()
            for branch in pushBranches:
                cmds += self.__git.push(remote, branch, True)

            if not opts.notags:
                pushTags = opts.getTagsToPush()
                for tag in pushTags:
                    cmds += self.__git.push(remote, tag, True)

            if len(cmds) > 0:
                e = self.__git.run(cmds, self.out)
                if e != 0:
                    return e
        return 0

    def clone(self, remote, opts):
        for url in self.remotes:
            self.__git.addRemote(remote, url)
            opts = gitoptions.GitOptions(remote, opts, self.__git)
            e = self.__git.clone(remote, self.path, opts.bare)
            if e == 0:
                return 0
        return -1
