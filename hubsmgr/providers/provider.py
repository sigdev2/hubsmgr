#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os

class Provider:
    __slots__ = (r'path', r'out')

    def __init__(self, path, out = None):
        self.path = path
        self.out = out
    
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
        return os.path.exists(self.path) and os.path.isdir(self.path) and (len(os.listdir(self.path)) > 0)
    
    def addRemotes(self, remoteName, remotes):
        pass
    
    def commit(self, message, addAll):
        return -1

    def pull(self, remote, opts):
        return -1
    
    def push(self, remote, opts):
        return -1
    
    def clone(self, remote, opts):
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

            if out == None:
                return process.wait()
            out(cmd, True)
            while True:
                line = process.stdout.readline().strip()
                exitCode = process.poll()
                if (line == r'') and not(exitCode is None):
                    return exitCode
                if line != r'':
                    out(line, False)
        return 0