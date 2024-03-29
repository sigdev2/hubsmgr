#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

class Provider:
    __slots__ = (r'path', r'out', r'remotes')

    def __init__(self, path, out = None):
        self.path = path
        self.out = out
        self.remotes = {}

    def isPullSupport(self):
        return False

    def isPushSupport(self):
        return False

    def isCommitSupport(self):
        return False

    def isCloneSupport(self):
        return False

    def isValid(self):
        return False

    def isExist(self):
        return self.path.exists() and \
               self.path.is_dir() and \
               any(self.path.iterdir())

    def addRemotes(self, remoteName, remotes):
        if not remoteName in self.remotes:
            self.remotes[remoteName] = set()
        for remote in remotes:
            self.remotes[remoteName].add(remote)

    def commit(self, message, addAll): # pylint: disable=unused-argument
        return -1

    def pull(self, remote, opts): # pylint: disable=unused-argument
        return -1

    def push(self, remote, opts): # pylint: disable=unused-argument
        return -1

    def clone(self, remote, opts): # pylint: disable=unused-argument
        return -1

    def run(self, cmd, out, cwd):
        if isinstance(cmd, list):
            for c in cmd:
                ec = self.run(c, out, cwd)
                if ec != 0:
                    return ec
        elif callable(cmd):
            return self.run(cmd(), out, cwd)
        elif len(cmd) > 0:
            process = subprocess.Popen(
                cmd,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                encoding=r'utf-8',
                errors=r'replace'
            )

            if out is None:
                return process.wait()
            out(cmd, True)
            while True:
                line = process.stdout.readline().strip()
                exitCode = process.poll()
                if line == r'' and not exitCode is None:
                    return exitCode
                if line != r'':
                    out(line, False)
        return 0
