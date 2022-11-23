#!/usr/bin/env python
# -*- coding: utf-8 -*-

from providers.provider import Provider
import os
import re

GIT_SIGN = r'.git'

def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True

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

    ######
    
    def __updateChanges(self):
        self.opts.hasChanges = self.__hasChanges()

    def __updateBranchesAndTags(self):
        self.opts.currentBranch = self.__getCurrentBranch()
        self.opts.localBranches = self.__getLocalBranches()
        self.opts.remoteBranches = self.__getRemoteBranches(self.opts.remoteName)
        self.opts.currentRevinsion = self.__getRevision(r'HEAD')
        realBranches = set(self.opts.localBranches.keys()).union(self.opts.remoteBranches.keys())
        self.opts.branches = realBranches.intersection(self.opts.arguments)

        if not(self.opts.notags):
            self.opts.localTags = self.__getLocalTags()
            self.opts.remoteTags = self.__getRemoteTags(self.opts.remoteName)
            realTags = set(self.opts.localTags.keys()).union(self.opts.remoteTags.keys())
            self.opts.tags = realTags.intersection(self.opts.arguments)

    def __hasChanges(self):
        hasChanges = [False]
        def inserter(line, isCommand):
            if not(isCommand) and len(line) > 0:
                hasChanges[0] = True
        if self.run(r'git status --porcelain', inserter, self.path()) != 0:
            return False
        return hasChanges[0]
    
    def __getRemoteUrl(self, remote):
        url = [r'']
        def inserter(line, isCommand):
            if not(isCommand):
                url[0] = line
        if self.run(r'git config --get remote.' + remote + r'.url ', inserter, self.path()) != 0:
            return r''
        return url[0]

    def __hasRemote(self, remote):
        hasRemote = [False]
        def checker(existRemote, isCommand):
            if not(isCommand):
                hasRemote[0] = hasRemote[0] or existRemote == remote
        if self.run(r'git remote', checker, self.path()) != 0:
            return False
        return hasRemote[0]
    
    def __getRevision(self, tag):
        revision = [r'']
        def inserter(line, isCommand):
            if not(isCommand):
                revision[0] = line
        if self.run(r'git rev-parse ' + tag, inserter, self.path()) != 0:
            return r''
        return revision[0]

    def __getLocalBranches(self):
        branches = {}
        regex = r'([^\s\*]+)'
        def inserter(line, isCommand):
            if not(isCommand) and not(r'HEAD detached' in line):
                matches = re.finditer(regex, line)
                for matchNum, match in enumerate(matches, start=1):
                    branch = match.group(1)
                    branches[branch] = self.__getRevision(branch)
        if self.run(r'git branch', inserter, self.path()) != 0:
            return {}
        return branches
    
    def __getLocalTags(self):
        tags = {}
        def inserter(tag, isCommand):
            if not(isCommand):
                tags[tag] = self.__getRevision(tag)
        if self.run(r'git tag', inserter, self.path()) != 0:
            return {}
        return tags
    
    def __getRemoteBranches(self, remote):
        branches = {}
        regex = r'([^\s]+)\s*refs/heads/([^\s]+)'
        def inserter(line, isCommand):
            if not(isCommand):
                matches = re.finditer(regex, line)
                for matchNum, match in enumerate(matches, start=1):
                    hash = match.group(1)
                    branch = match.group(2)
                    branches[branch] = hash
        
        if self.run(r'git ls-remote -h ' + remote, inserter, self.path()) !=0:
            return {}
        return branches
    
    def __getRemoteTags(self, remote):
        tags = {}
        regex = r'([^\s]+)\s*refs/tags/([^\s]+)'
        def inserter(line, isCommand):
            if not(isCommand):
                matches = re.finditer(regex, line)
                for matchNum, match in enumerate(matches, start=1):
                    hash = match.group(1)
                    branch = match.group(2)
                    tags[branch] = hash
        
        if self.run(r'git ls-remote --tags ' + remote, inserter, self.path()) !=0:
            return {}
        return tags

    def __getCurrentBranch(self):
        current = [r'']
        def inserter(line, isCommand):
            if not(isCommand):
                current[0] = line
        if self.run(r'git branch --show-current', inserter, self.path()) != 0:
            return r''
        return current[0]
    
    def __getObjectType(self, hash):
        type = [r'']
        def inserter(line, isCommand):
            if not(isCommand):
                type[0] = line
        if self.run(r'git cat-file -t ' + hash, inserter, self.path()) != 0:
            return r''
        return type[0]
    
    def __getTagType(self, tag):
        type = [r'']
        def inserter(line, isCommand):
            if not(isCommand) and line.startswith(r'type '):
                type[0] = line[5:]
        if self.run(r'git cat-file -p ' + tag, inserter, self.path()) != 0:
            return r''
        return type[0]
    
    def __checkoutCommands(self):
        cmds = []

        freeTags = set()
        if not(self.opts.notags):
            for tag in self.opts.actualTags():
                tagType = self.__getObjectType(tag)
                if tagType == r'tag':
                    tagType = self.__getTagType(tag)
                if tagType != r'commit':
                    freeTags.add(tag)

        def checkoutCurrent():
            curretnRevision = self.__getRevision(r'HEAD')
            if len(self.opts.revisions) > 0:
                if curretnRevision != self.opts.currentRevinsion and self.opts.currentRevinsion in self.opts.revisions:
                    return r'git checkout ' + self.opts.currentRevinsion
                if not(curretnRevision in self.opts.revisions):
                    return r'git checkout ' + list(self.opts.revisions)[0]
                return r''
            if not(self.opts.notags):
                fixedTags = self.opts.tags.difference(freeTags)
                if len(fixedTags) > 0:
                    tags = {}
                    tagForCurrent = None
                    for tag in fixedTags:
                        if tag in self.opts.remoteTags:
                            tags[tag] = self.opts.remoteTags[tag]
                        elif tag in self.opts.localTags:
                            tags[tag] = self.opts.localTags[tag]
                        if (tag in tags) and (tags[tag] == self.opts.currentRevinsion):
                            tagForCurrent = tag

                    if (curretnRevision != self.opts.currentRevinsion) and (tagForCurrent != None):
                        return r'git checkout ' + tagForCurrent
                    if not(curretnRevision in tags.values()):
                        return r'git checkout ' + list(tags.keys())[0]
                    return r''

            if len(self.opts.branches) > 0:
                branches = {}
                for branch in self.opts.branches:
                    if branch in self.opts.remoteBranches:
                        branches[branch] = self.opts.remoteBranches[branch]
                    elif branch in self.opts.localBranches:
                        branches[branch] = self.opts.localBranches[branch]

                if (curretnRevision != self.opts.currentRevinsion) and len(self.opts.currentBranch) > 0 and (self.opts.currentBranch in branches):
                    return r'git checkout ' + self.opts.currentBranch
                if not(curretnRevision in branches.values()):
                    return r'git checkout ' + list(branches.keys())[0]
                return r''
            
            if curretnRevision != self.opts.currentRevinsion:
                if len(self.opts.currentBranch) > 0:
                    return r'git checkout ' + self.opts.currentBranch
                return r'git checkout ' + self.opts.currentRevinsion
            return r''

        cmds.append(checkoutCurrent)

        if not(self.opts.notags):
            for tag in freeTags.intersection(self.opts.tags):
                cmds.append(r'git checkout ' + tag + r' .')
        
        if not(self.opts.nosubmodules):
            cmds.append(r'git submodule update --init --recursive --remote')
        
        return cmds