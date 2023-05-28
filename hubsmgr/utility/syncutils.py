#!/usr/bin/env python
# -*- coding: utf-8 -*-

def getPulPushOptions(opts):
    hasPull = r'pull' in opts
    hasPush = r'push' in opts
    return (hasPull or not hasPush), (hasPush or not hasPull)

class SyncUnit:
    __slots__ = (r'remote', r'provider')

    def __init__(self, remote, provider):
        self.remote = remote
        self.provider = provider

def cloneCommand(unit, opts):
    if unit.provider.isExist():
        return 0
    unit.provider.out(r' <- Clone from ' + unit.remote + r' to ' + str(unit.provider.path), False)
    return unit.provider.clone(unit.remote, opts)

def commitCommand(unit, opts): # pylint: disable=unused-argument
    unit.provider.out(r' * Auto commit in ' + str(unit.provider.path), False)
    return unit.provider.commit(r'auto commit', True)

def pullCommand(unit, opts):
    unit.provider.out(r' <- Pull from ' + unit.remote + r' (' + str(unit.provider.path) + r')', False)
    return unit.provider.pull(unit.remote, opts)

def pushCommand(unit, opts):
    unit.provider.out(r' -> Push to ' + unit.remote + r' (' + str(unit.provider.path) + r')', False)
    return unit.provider.push(unit.remote, opts)

class SyncObject:
    __slots__ = (r'__permissions', r'__value', r'__commands')

    def __init__(self, permissions, value, commands):
        self.__permissions = permissions
        self.__value = value
        self.__commands = commands

    def merge(self, permissions):
        self.__permissions = [permissions[i] and v for i, v in enumerate(self.__permissions)]
        return self

    def check(self, i):
        return self.__permissions[i]

    def exec(self, i, arguments):
        return self.__commands[i](self.__value, *arguments)

class SyncCommands:
    __slots__ = (r'__order', r'__commands')

    def __init__(self, commands):
        self.__order = tuple([] for _ in range(len(commands)))
        self.__commands = commands

    def create(self, permissions, value):
        return SyncObject(permissions, value, self.__commands)

    def add(self, obj):
        for i, objs in enumerate(self.__order):
            if obj.check(i):
                objs.append(obj)

    def clear(self):
        self.__order = tuple([] for _ in range(len(self.__commands)))

    def exec(self, arguments):
        for i, objs in enumerate(self.__order):
            for obj in objs:
                e = obj.exec(i, arguments)
                if e != 0:
                    self.clear()
                    return e
        self.clear()
        return 0

PROVIDER_CMDS = SyncCommands([cloneCommand,
                              commitCommand,
                              pullCommand,
                              pushCommand])
