#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ProviderProxy:
    __slots__ = (r'source',)

    def __init__(self, source):
        self.source = source

    def __getattr__(self, name):
        if name == r'source':
            return object.__getattribute__(self, name)
        return self.source.__getattribute__(name)

    def __setattr__(self, name, value):
        if name == r'source':
            return object.__setattr__(self, name, value)
        return self.source.__setattr__(name, value)

    def baseType(self):
        if isinstance(self.source, ProviderProxy):
            return self.source.baseType()
        return type(self.source)
