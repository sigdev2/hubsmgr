#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        self.__order = tuple([] for _ in range(self.__commands))

    def exec(self, arguments):
        for i, objs in enumerate(self.__order):
            for obj in objs:
                if obj.exec(i, arguments) == -1:
                    self.clear()
                    return -1
        self.clear()
        return 0
