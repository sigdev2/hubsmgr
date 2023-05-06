#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gitoptions
            
class GitOptions:
    __slots__ = [r'nosubmodules',
                 r'unrelated',
                 r'notags',
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
    
    def branchesToPull(self):
        branches = {}

        localBranches = self.git.getLocalBranches()
        remoteBranches = self.git.getRemoteBranches(self.remoteName)

        checkBranches = remoteBranches if self.isEmpty() else set(remoteBranches.keys()).intersection(self.branches)
        for branch in checkBranches:
            if not(branch in localBranches):
                branches[branch] = True
            elif self.remoteBranches[branch] != self.localBranches[branch]:
                branches[branch] = False
        return branches

    def branchesToPush(self):
        branches = {}
        remoteBranches = self.remoteBranches.keys()
        checkBranches = self.localBranches if self.isSyncAll() else set(self.localBranches.keys()).intersection(self.branches)
        for branch in checkBranches:
            if not(branch in remoteBranches):
                branches[branch] = True
            elif self.remoteBranches[branch] != self.localBranches[branch]:
                branches[branch] = False
        return branches
    
    def tagsToPull(self):
        tags = {}
        localTags = self.localTags.keys()
        checkTags = self.remoteTags if self.isSyncAll() else set(self.remoteTags.keys()).intersection(self.tags)
        for tag in checkTags:
            if not(tag in localTags):
                tags[tag] = True
            elif self.remoteTags[tag] != self.localTags[tag]:
                tags[tag] = False
        return tags

    def tagsToPush(self):
        tags = {}
        remoteTags = self.remoteTags.keys()
        checkTags = self.localTags if self.isSyncAll() else set(self.localTags.keys()).intersection(self.tags)
        for tag in checkTags:
            if not(tag in remoteTags):
                tags[tag] = True
            elif self.remoteTags[tag] != self.localTags[tag]:
                tags[tag] = False
        return tags