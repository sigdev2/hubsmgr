#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os

class Hub:
    __slots__ = [r'provider', r'id', r'paths', r'urls', r'opts']

    def __init__(self, provider, id, paths, urls, opts):
        self.provider = provider
        self.id = id
        self.paths = paths
        self.urls = urls
        self.opts = opts

class HubsParser:
    __slots__ = [r'hubs']

    HUBS_PROVIDERS = [r'git', r'pysync']
    HUBS_OPTIONS = [r'pull', r'push', r'freeze', r'managed']

    def __init__(self):
        self.hubs = dict()

    def check(self, path):
        return re.match(r'^/hubs/[A-z_-]+', path)
        
    def hubIsPath(self, url):
        return re.match(r'^(windrives://|file://|[A-z]:|\.\/|\.\.\/|\/|\\)', url)

    def process(self, hubList, hubName):
        if not(type(hubList) is list):
            hubList = hubList.split()

        findProviders = set(hubList).intersection(set(HubsParser.HUBS_PROVIDERS))
        if len(findProviders) == 0:
            findProviders = { HubsParser.HUBS_PROVIDERS[0] }
        findUrlsWithOpts = set(hubList) - set(HubsParser.HUBS_PROVIDERS)

        options = set(findUrlsWithOpts).intersection(set(HubsParser.HUBS_OPTIONS))
        if len(options) == 0:
            options = { HubsParser.HUBS_OPTIONS[0], HubsParser.HUBS_OPTIONS[1] }

        findUrls = set(findUrlsWithOpts) - set(HubsParser.HUBS_OPTIONS)

        urls = set()
        paths = set()
        for url in findUrls:
            if self.hubIsPath(url):
                if url.startswith(r'file://'):
                    url = url[7:]
                if url.startswith(r'windrives://'):
                    path = url[12:]
                    url = [ x + r':/' + path for x in r'QWERTYUIOPASDFGHJKLZXCVBNM' ]
                else:
                    url = [url]
                for u in url:
                    absPath = os.path.abspath(u)
                    if absPath[-1] != os.sep:
                        if absPath[-1] == r'/' or absPath[-1] == r'\\':
                            absPath[-1] = os.sep
                        else:
                            absPath += os.sep
                    if os.path.exists(absPath):
                        paths.add(absPath)
            else:
                if url[-1] != r'/':
                    if url[-1] == r'\\':
                        url[-1] = r'/'
                    else:
                        url += r'/'
                urls.add(url)

        if (len(urls) == 0) and (len(paths) == 0):
            return True
        
        self.hubs[hubName] = Hub(list(findProviders)[0], hubName, paths, urls, options)
        return True
