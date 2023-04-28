#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ParseItem:
    __slots__ = [r'id', r'parameters']

    def __init__(self, id, parameters):
        self.id = id
        self.parameters = parameters