#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

class Provider:
    __slots__ = [r'hub', r'name', r'url', r'root', r'out', r'opts']

    def __init__(self, hub, name, url, root, out = None):
        self.hub = hub
        self.name = name
        self.url = url
        self.root = root
        self.out = out
        self.opts = set()
    
    def updateRemotes(self):
        return -1
    
    def path(self):
        return self.root / self.name

    def remoteName(self):
        return self.hub + r'_' + self.name
    
    def isExist(self):
        p = self.path()
        return p.exists() and p.is_dir()

    def setOptions(self, val):
        self.opts = val

    def commit(self, message, addAll):
        return -1

    def pull(self):
        return -1
    
    def push(self):
        return -1
    
    def clone(self):
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