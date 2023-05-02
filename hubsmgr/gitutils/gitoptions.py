#!/usr/bin/env python
# -*- coding: utf-8 -*-

class GitOptions:
    __slots__ = [r'remoteName', r'localBranches', r'remoteBranches', r'localTags', r'remoteTags', r'currentBranch', r'currentRevinsion', r'branches', r'tags', r'revisions', r'notags', r'nosubmodules', r'hasChanges', r'unrelated', r'arguments']
    def __init__(self):
        self.remoteName = r''
        self.notags = False
        self.nosubmodules = False
        self.unrelated = False
        self.hasChanges = False
        self.currentBranch = {}
        self.localBranches = {}
        self.remoteBranches = {}
        self.currentRevinsion = r''
        self.branches = set()
        self.revisions = set()
        self.localTags = {}
        self.remoteTags = {}
        self.tags = set()
        self.arguments = set()
    
    @staticmethod
    def isNetSupport():
        return True
    
    def hasLegalFixedChekout(self):
        fixedRevisionsOrTag = set(self.remoteTags.values()).union(set(self.localTags.values())).union(self.revisions)
        return self.currentRevinsion in fixedRevisionsOrTag
    
    def canCommit(self):
        if len(self.currentBranch) <= 0:
            return False
        if self.hasLegalFixedChekout():
            return False
        if not(self.hasChanges):
            return False
        return True
    
    def isSyncAll(self):
        return (len(self.branches) <= 0) and (len(self.tags) <= 0) and (len(self.revisions) <= 0)
    
    def branchesToPull(self):
        branches = {}
        localBranches = self.localBranches.keys()
        checkBranches = self.remoteBranches if self.isSyncAll() else set(self.remoteBranches.keys()).intersection(self.branches)
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
    
    def actualTags(self):
        return self.tags.intersection(set(self.remoteTags.keys()).union(set(self.localTags.keys())))
    
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