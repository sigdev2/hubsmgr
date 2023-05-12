#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gitutils import sha1utils

class GitOptions:
    __slots__ = (r'nosubmodules',
                 r'unrelated',
                 r'notags',
                 r'bare',
                 r'revisions',
                 r'branches',
                 r'tags',
                 r'git',
                 r'remoteName')

    def __init__(self, remoteName, textOpts, git):
        self.git = git
        self.remoteName = remoteName

        localBranches = self.git.getLocalBranches()
        remoteBranches = self.git.getRemoteBranches(self.remoteName)
        realBranches = set(localBranches.keys()).union(remoteBranches.keys())

        self.notags = False
        self.nosubmodules = False
        self.unrelated = False
        self.bare = False

        self.revisions = set()
        arguments = set()
        for opt in textOpts:
            if sha1utils.is_sha1(opt):
                self.revisions.add(opt)
            elif opt == r'notags':
                self.notags = True
            elif opt == r'nosub':
                self.nosubmodules = True
            elif opt == r'unrelated':
                self.unrelated = True
            elif opt == r'bare':
                self.bare = True
            else:
                arguments.add(opt)

        self.branches = realBranches.intersection(arguments)
        self.tags = set()

        if not self.notags:
            localTags = self.git.getLocalTags()
            remoteTags = self.git.getRemoteTags(self.remoteName)
            realTags = set(localTags.keys()).union(remoteTags.keys())
            self.tags = realTags.intersection(arguments)

    def isEmpty(self):
        return (len(self.branches) <= 0) and (len(self.tags) <= 0) and (len(self.revisions) <= 0)

    def getBranchesToPull(self):
        return self.__getItems(self.git.getRemoteBranches(self.remoteName),
                               self.git.getLocalBranches(), self.branches)

    def getBranchesToPush(self):
        return self.__getItems(self.git.getLocalBranches(),
                               self.git.getRemoteBranches(self.remoteName), self.branches)

    def getTagsToPull(self):
        if self.notags:
            return {}
        return self.__getItems(self.git.getRemoteTags(self.remoteName),
                               self.git.getLocalTags(), self.tags)

    def getTagsToPush(self):
        if self.notags:
            return {}
        return self.__getItems(self.git.getLocalTags(),
                               self.git.getRemoteTags(self.remoteName), self.tags)

    def getAllFreeTags(self):
        if self.notags:
            return {}
        localTags = self.git.getLocalTags()
        remoteTags = self.git.getRemoteTags(self.remoteName)
        realTags = set(localTags.keys()).union(remoteTags.keys())
        freeTags = set()
        for tag in realTags:
            tagType = self.git.getObjectType(tag)
            if tagType == r'tag':
                tagType = self.git.getTagType(tag)
            if tagType != r'commit':
                freeTags.add(tag)
        return freeTags

    def getRealTagsRevisions(self, tags):
        localTags = self.git.getLocalTags()
        remoteTags = self.git.getRemoteTags(self.remoteName)
        revisions = {}
        for tag in tags:
            if tag in remoteTags:
                revisions[tag] = remoteTags[tag]
            elif tag in localTags:
                revisions[tag] = localTags[tag]
        return revisions

    def getRealBranchesRevisions(self, branches):
        localBranches = self.git.getLocalBranches()
        remoteBranches = self.git.getRemoteBranches(self.remoteName)
        revisions = {}
        for branch in branches:
            if branch in remoteBranches:
                revisions[branch] = remoteBranches[branch]
            elif branch in localBranches:
                revisions[branch] = localBranches[branch]
        return revisions

    def getRealBranchRevision(self, branch):
        revisions = self.getRealBranchesRevisions([branch])
        if len(revisions) <= 0:
            return r''
        return revisions[branch]

    def __getItems(self, fromItems, toItems, filterItems):
        items = {}
        checkItems = fromItems \
                     if self.isEmpty() \
                     else set(fromItems.keys()).intersection(filterItems)
        for item in checkItems:
            isNew = not item in toItems
            if isNew or fromItems[item] != toItems[item]:
                items[item] = isNew
        return items
