#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ProviderProxy:
    __slots__ = (r'source',)

    def __init__(self, source):
        self.source = source

    def __getattr__(self, name):
        return self.source.__getattribute__(name)

    def baseType(self):
        if isinstance(self.source, ProviderProxy):
            return self.source.baseType()
        return type(self.source)
