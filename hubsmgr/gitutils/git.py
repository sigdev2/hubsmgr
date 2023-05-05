#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pathlib
import os

class Git:
    __slots__ = [r'path', r'run']
    
    GIT_DIR = r'.git'

    BRANCH_NAME_RX = re.compile(r'([^\s\*]+)')
    REMOTE_BRANCH_RX = re.compile(r'([^\s]+)\s*refs/heads/([^\s]+)')
    REMOTE_TAG_RX = re.compile(r'([^\s]+)\s*refs/tags/([^\s]+)')

    def __init__(self, path, run, out):
        self.path = path
        self.out = out
        self.run = lambda cmd, callback, cd = None: run(cmd, callback, self.path if cd == None else cd)
    
    # path

    def isRepository(self):
        gitSignPath = pathlib.path(self.path) / Git.GIT_DIR
        return gitSignPath.exists() and gitSignPath.is_dir() and (len(os.listdir(gitSignPath)) > 0)
    
    # objects

    def getRevision(self, item):
        revision = [r'']
        def inserter(line, isCommand):
            if not(isCommand):
                revision[0] = line
        if self.run(r'git rev-parse ' + item, inserter) != 0:
            return r''
        return revision[0]
    
    def getObjectType(self, hash):
        type = [r'']
        def inserter(line, isCommand):
            if not(isCommand):
                type[0] = line
        if self.run(r'git cat-file -t ' + hash, inserter) != 0:
            return r''
        return type[0]
    
    # changes

    def hasChanges(self):
        hasChanges = [False]
        def inserter(line, isCommand):
            if not(isCommand) and len(line) > 0:
                hasChanges[0] = True
        if self.run(r'git status --porcelain', inserter) != 0:
            return False
        return hasChanges[0]
    
    # branches
    
    def getCurrentBranch(self):
        current = [r'']
        def inserter(line, isCommand):
            if not(isCommand):
                current[0] = line
        if self.run(r'git branch --show-current', inserter) != 0:
            return r''
        return current[0]
    
    def getLocalBranches(self):
        branches = {}
        def inserter(line, isCommand):
            if not(isCommand) and not(r'HEAD detached' in line):
                matches = Git.BRANCH_NAME_RX.finditer(line)
                for matchNum, match in enumerate(matches, start=1):
                    branch = match.group(1)
                    branches[branch] = self.getRevision(branch)
        if self.run(r'git branch', inserter) != 0:
            return {self}
        return branches
    
    def getRemoteBranches(self, remoteName):
        branches = {}
        def inserter(line, isCommand):
            if not(isCommand):
                matches = Git.REMOTE_BRANCH_RX.finditer(line)
                for matchNum, match in enumerate(matches, start=1):
                    hash = match.group(1)
                    branch = match.group(2)
                    branches[branch] = hash
        
        if self.run(r'git ls-remote -h ' + remoteName, inserter) !=0:
            return {}
        return branches

    def getCurrentBranch(self):
        current = [r'']
        def inserter(line, isCommand):
            if not(isCommand):
                current[0] = line
        if self.run(r'git branch --show-current', inserter) != 0:
            return r''
        return current[0]
    
    # tags

    def getLocalTags(self):
        tags = {}
        def inserter(tag, isCommand):
            if not(isCommand):
                tags[tag] = self.getRevision(tag)
        if self.run(r'git tag', inserter) != 0:
            return {}
        return tags
    
    def getRemoteTags(self, remote):
        tags = {}
        def inserter(line, isCommand):
            if not(isCommand):
                matches = Git.REMOTE_TAG_RX.finditer(line)
                for matchNum, match in enumerate(matches, start=1):
                    hash = match.group(1)
                    branch = match.group(2)
                    tags[branch] = hash
        
        if self.run(r'git ls-remote --tags ' + remote, inserter) !=0:
            return {}
        return tags
    
    def getTagType(self, tag):
        type = [r'']
        def inserter(line, isCommand):
            if not(isCommand) and line.startswith(r'type '):
                type[0] = line[5:]
        if self.run(r'git cat-file -p ' + tag, inserter) != 0:
            return r''
        return type[0]

    # remotes

    def getRemoteUrl(self, remoteName):
        url = [r'']
        def inserter(line, isCommand):
            if not(isCommand):
                url[0] = line
        if self.run(r'git config --get remote.' + remoteName + r'.url ', inserter) != 0:
            return r''
        return url[0]

    def hasRemote(self, remoteName):
        hasRemote = [False]
        def checker(existRemote, isCommand):
            if not(isCommand):
                hasRemote[0] = hasRemote[0] or existRemote == remoteName
        if self.run(r'git remote', checker) != 0:
            return False
        return hasRemote[0]
    
    def addRemote(self, remoteName, url):
        if not(self.hasRemote(remoteName)):
            ec = self.run(r'git remote add ' + remoteName + r' ' + url, self.out)
            if ec != 0:
                return ec
        elif self.getRemoteUrl(remoteName) != url:
            ec = self.run(r'git remote set-url ' + remoteName + r' ' + url, self.out)
            if ec != 0:
                return ec
        return 0
    
    # operations

    def checkout(self, remoteName, tagOrBranchOrRevision, getCommands = False):
        cmds = [r'git checkout ' + remoteName + r' ' + tagOrBranchOrRevision]
        if getCommands:
            return cmds
        return self.run(cmds, self.out)

    def fetch(self, remoteName, tagOrBranchOrRevision, getCommands = False):
        cmds = [r'git fetch ' + remoteName + r' ' + tagOrBranchOrRevision]
        if getCommands:
            return cmds
        return self.run(cmds, self.out)
    
    def merge(self, remoteName, branch, unrelated, getCommands = False):
        cmds = [r'git merge ' + (r'--allow-unrelated-histories ' if unrelated else r'') + remoteName + r'/' + branch]
        if getCommands:
            return cmds
        return self.run(cmds, self.out)

    def pull_branch_with_checkout(self, remoteName, branch, isNew, unrelated, getCommands = False):
        cmds = [self.fetch(remoteName, branch + (r':' + branch if isNew else r''), True)[0]]
        if not(isNew):
            cmds.append(lambda : self.checkout(remoteName, branch, True)[0] if self.getCurrentBranch() != branch else r'')
            cmds.append(self.merge(remoteName, branch, unrelated, True)[0])
        if getCommands:
            return cmds
        return self.run(cmds, self.out)

    def pull_tag(self, remoteName, tag, getCommands = False):
        return self.fetch(self, remoteName, tag, getCommands)

    def push(self, remoteName, tagOrBranch, getCommands = False):
        cmds = [r'git push ' + remoteName + r' ' + tagOrBranch + r':' + tagOrBranch]
        if getCommands:
            return cmds
        return self.run(cmds, self.out)
        
    def clone(self, remoteName, url, getCommands = False):
        p = pathlib.Path(self.path)
        name = p.parts[-1]
        opts = r' -o ' + remoteName
        opts += r' ' + url
        opts += r' .' + os.sep + name + os.sep
        cmds = [r'git clone' + opts]
        if getCommands:
            return cmds
        return self.run(cmds, self.out, p.parent)
    
    def updateSubmodules(self, getCommands = False):
        cmds = [r'git submodule update --init --recursive --remote']
        if getCommands:
            return cmds
        return self.run(cmds, self.out)