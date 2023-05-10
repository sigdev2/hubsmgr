#!/usr/bin/env python
# -*- coding: utf-8 -*-

def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        _ = int(maybe_sha, 16)
    except ValueError:
        return False
    return True
