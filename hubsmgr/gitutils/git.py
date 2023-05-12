#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pathlib
import os

from utility.memoized_method import weak_lru

class Git:
    __slots__ = (r'__path', r'__out', r'__run')

    GIT_DIR = r'.git'
    GIT_SUBDIRS = (r'hooks', r'info', r'objects', r'logs', r'refs')

    BRANCH_NAME_RX = re.compile(r'([^\s\*]+)')
    REMOTE_BRANCH_RX = re.compile(r'([^\s]+)\s*refs/heads/([^\s]+)')
    REMOTE_TAG_RX = re.compile(r'([^\s]+)\s*refs/tags/([^\s]+)')

    def __init__(self, path, run, out):
        self.__path = path
        self.__out = out
        self.__run = run

    def run(self, cmd, callback, cd = None):
        return self.__run(cmd, callback, self.__path if cd is None else cd)

    # path

    @weak_lru(maxsize=None)
    def isRepository(self, bare):
        root = pathlib.Path(self.__path)
        for subdir in Git.GIT_SUBDIRS:
            if not bare:
                subdir = Git.GIT_DIR + os.sep + subdir
            gitSignPath = root / subdir
            if not gitSignPath.exists() or not gitSignPath.is_dir():
                return False
        return True

    # objects

    @weak_lru(maxsize=None)
    def getRevision(self, item):
        revision = [r'']
        def inserter(line, isCommand):
            if not isCommand:
                revision[0] = line
        if self.run(r'git rev-parse ' + item, inserter) != 0:
            return r''
        return revision[0]

    @weak_lru(maxsize=None)
    def getObjectType(self, objhash):
        objtype = [r'']
        def inserter(line, isCommand):
            if not isCommand:
                objtype[0] = line
        if self.run(r'git cat-file -t ' + objhash, inserter) != 0:
            return r''
        return objtype[0]

    # changes

    @weak_lru(maxsize=None)
    def hasChanges(self):
        hasChanges = [False]
        def inserter(line, isCommand):
            if not(isCommand) and len(line) > 0:
                hasChanges[0] = True
        if self.run(r'git status --porcelain', inserter) != 0:
            return False
        return hasChanges[0]

    # branches

    @weak_lru(maxsize=None)
    def getCurrentBranch(self):
        current = [r'']
        def inserter(line, isCommand):
            if not isCommand:
                current[0] = line
        if self.run(r'git branch --show-current', inserter) != 0:
            return r''
        return current[0]

    @weak_lru(maxsize=None)
    def getLocalBranches(self):
        branches = {}
        def inserter(line, isCommand):
            if not isCommand and not r'HEAD detached' in line:
                matches = Git.BRANCH_NAME_RX.finditer(line)
                for _, match in enumerate(matches, start=1):
                    branch = match.group(1)
                    branches[branch] = self.getRevision(branch)
        if self.run(r'git branch', inserter) != 0:
            return {self}
        return branches

    @weak_lru(maxsize=None)
    def getRemoteBranches(self, remoteName):
        branches = {}
        def inserter(line, isCommand):
            if not isCommand:
                matches = Git.REMOTE_BRANCH_RX.finditer(line)
                for _, match in enumerate(matches, start=1):
                    objhash = match.group(1)
                    branch = match.group(2)
                    branches[branch] = objhash

        if self.run(r'git ls-remote -h ' + remoteName, inserter) !=0:
            return {}
        return branches

    # tags

    @weak_lru(maxsize=None)
    def getLocalTags(self):
        tags = {}
        def inserter(tag, isCommand):
            if not isCommand:
                tags[tag] = self.getRevision(tag)
        if self.run(r'git tag', inserter) != 0:
            return {}
        return tags

    @weak_lru(maxsize=None)
    def getRemoteTags(self, remote):
        tags = {}
        def inserter(line, isCommand):
            if not isCommand:
                matches = Git.REMOTE_TAG_RX.finditer(line)
                for _, match in enumerate(matches, start=1):
                    objhash = match.group(1)
                    branch = match.group(2)
                    tags[branch] = objhash

        if self.run(r'git ls-remote --tags ' + remote, inserter) !=0:
            return {}
        return tags

    @weak_lru(maxsize=None)
    def getTagType(self, tag):
        objtype = [r'']
        def inserter(line, isCommand):
            if not(isCommand) and line.startswith(r'type '):
                objtype[0] = line[5:]
        if self.run(r'git cat-file -p ' + tag, inserter) != 0:
            return r''
        return objtype[0]

    # remotes

    @weak_lru(maxsize=None)
    def getRemoteUrl(self, remoteName):
        url = [r'']
        def inserter(line, isCommand):
            if not isCommand:
                url[0] = line
        if self.run(r'git config --get remote.' + remoteName + r'.url ', inserter) != 0:
            return r''
        return url[0]

    @weak_lru(maxsize=None)
    def hasRemote(self, remoteName):
        hasRemote = [False]
        def checker(existRemote, isCommand):
            if not isCommand:
                hasRemote[0] = hasRemote[0] or existRemote == remoteName
        if self.run(r'git remote', checker) != 0:
            return False
        return hasRemote[0]

    def addRemote(self, remoteName, url):
        def clearCahche():
            self.clearRemotesCache()
            self.clearRemotesObjectsCache()
            self.clearObjectsCache()
        if not self.hasRemote(remoteName):
            ec = self.run(r'git remote add ' + remoteName + r' ' + url, self.__out)
            if ec != 0:
                return ec
            clearCahche()
        elif self.getRemoteUrl(remoteName) != url:
            ec = self.run(r'git remote set-url ' + remoteName + r' ' + url, self.__out)
            if ec != 0:
                return ec
            clearCahche()
        return 0

    # operations

    def checkout(self, remoteName, tagOrBranchOrRevision, getCommands = False):
        def cmd():
            self.clearCurrentBranchCache()
            self.clearChangesCache()
            return r'git checkout ' + remoteName + r' ' + tagOrBranchOrRevision
        if getCommands:
            return [cmd]
        return self.run(cmd, self.__out)

    def fetch(self, remoteName, tagOrBranchOrRevision, getCommands = False):
        def cmd():
            self.clearLocalObjectsCache()
            self.clearObjectsCache()
            return r'git fetch ' + remoteName + r' ' + tagOrBranchOrRevision
        if getCommands:
            return [cmd]
        return self.run(cmd, self.__out)

    def merge(self, remoteName, branch, unrelated, getCommands = False):
        def cmd():
            self.clearLocalObjectsCache()
            self.clearChangesCache()
            self.clearObjectsCache()
            return r'git merge ' + (r'--allow-unrelated-histories ' if unrelated else r'') + \
                   remoteName + r'/' + branch
        if getCommands:
            return [cmd]
        return self.run(cmd, self.__out)

    def pull_branch_with_checkout(self, remoteName, branch, isNew, unrelated, getCommands = False):
        cmds = [self.fetch(remoteName, branch + (r':' + branch if isNew else r''), True)[0]]
        if not isNew:
            cmds.append(lambda : self.checkout(remoteName, branch, True)[0]
                        if self.getCurrentBranch() != branch
                        else r'')
            cmds.append(self.merge(remoteName, branch, unrelated, True)[0])
        if getCommands:
            return cmds
        return self.run(cmds, self.__out)

    def pull_tag(self, remoteName, tag, getCommands = False):
        return self.fetch(remoteName, tag, getCommands)

    def push(self, remoteName, tagOrBranch, getCommands = False):
        def cmd():
            self.clearRemotesObjectsCache()
            self.clearObjectsCache()
            return r'git push ' + remoteName + r' ' + tagOrBranch + r':' + tagOrBranch
        if getCommands:
            return [cmd]
        return self.run(cmd, self.__out)

    def clone(self, remoteName, url, bare, getCommands = False):
        p = pathlib.Path(self.__path)
        name = p.parts[-1]
        opts = r'--bare' if bare else r''
        opts += r' -o ' + remoteName
        opts += r' ' + url
        opts += r' .' + os.sep + name + os.sep

        def cmd():
            self.clearAllCahce()
            return r'git clone' + opts
        if getCommands:
            return [cmd]
        return self.run(cmd, self.__out, p.parent)

    def commit(self, message, addAll, getCommands = False):
        cmds = []
        if addAll:
            def cmdAdd():
                self.clearLocalObjectsCache()
                self.clearChangesCache()
                self.clearObjectsCache()
                return r'git add -A'
            cmds.append(cmdAdd)
        def cmdCommit():
            self.clearLocalObjectsCache()
            self.clearChangesCache()
            self.clearObjectsCache()
            return r'git commit -m "' + message + r'"'
        cmds.append(cmdCommit)
        if getCommands:
            return cmds
        return self.run(cmds, self.__out)

    def updateSubmodules(self, getCommands = False):
        def cmd():
            self.clearObjectsCache()
            return r'git submodule update --init --recursive --remote'
        if getCommands:
            return [cmd]
        return self.run(cmd, self.__out)

    # cache cleaners

    def clearCurrentBranchCache(self):
        self.getCurrentBranch.__dict__[r'cache_clear']()

    def clearChangesCache(self):
        self.hasChanges.__dict__[r'cache_clear']()

    def clearObjectsCache(self):
        self.getObjectType.__dict__[r'cache_clear']()
        self.getTagType.__dict__[r'cache_clear']()
        self.getRevision.__dict__[r'cache_clear']()

    def clearRemotesObjectsCache(self):
        self.getRemoteTags.__dict__[r'cache_clear']()
        self.getRemoteBranches.__dict__[r'cache_clear']()

    def clearLocalObjectsCache(self):
        self.getLocalTags.__dict__[r'cache_clear']()
        self.getLocalBranches.__dict__[r'cache_clear']()

    def clearExistingsCache(self):
        self.isRepository.__dict__[r'cache_clear']()

    def clearRemotesCache(self):
        self.getRemoteUrl.__dict__[r'cache_clear']()
        self.hasRemote.__dict__[r'cache_clear']()

    def clearAllCahce(self):
        self.clearCurrentBranchCache()
        self.clearChangesCache()
        self.clearObjectsCache()
        self.clearRemotesObjectsCache()
        self.clearLocalObjectsCache()
        self.clearExistingsCache()
        self.clearRemotesCache()
