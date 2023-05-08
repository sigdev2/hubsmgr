#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gitoptions
            
class GitOptions:
    __slots__ = [r'nosubmodules',
                 r'unrelated',
                 r'notags',
                 r'bare',
                 r'revisions',
                 r'branches',
                 r'tags',
                 r'git',
                 r'remoteName']
    
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
            if gitoptions.is_sha1(opt):
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
        
        if not(self.notags):
            localTags = self.getLocalTags()
            remoteTags = self.getRemoteTags(self.remoteName)
            realTags = set(localTags.keys()).union(remoteTags.keys())
            self.tags = realTags.intersection(arguments)
    
    def isEmpty(self):
        return (len(self.branches) <= 0) and (len(self.tags) <= 0) and (len(self.revisions) <= 0)
    
    def getBranchesToPull(self):
        return self.__getItems(self.git.getRemoteBranches(self.remoteName), self.git.getLocalBranches(), self.branches)

    def getBranchesToPush(self):
        return self.__getItems(self.git.getLocalBranches(), self.git.getRemoteBranches(self.remoteName), self.branches)
    
    def getTagsToPull(self):
        if self.notags:
            return {}
        return self.__getItems(self.git.getRemoteTags(self.remoteName), self.git.getLocalTags(), self.tags)

    def getTagsToPush(self):
        if self.notags:
            return {}
        return self.__getItems(self.git.getLocalTags(), self.git.getRemoteTags(self.remoteName), self.tags)
    
    def __getItems(self, fromItems, toItems, filter):
        items = {}
        checkItems = fromItems if self.isEmpty() else set(fromItems.keys()).intersection(filter)
        for item in checkItems:
            isNew = not(item in toItems)
            if isNew or fromItems[item] != toItems[item]:
                items[item] = isNew
        return items
