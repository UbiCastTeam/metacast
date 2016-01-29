#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Utils for MetaCast.
'''
import re


def get_time_from_timecode(timecode_string):
    p = re.compile(r'(?P<h>\d{2}):(?P<m>\d{2}):(?P<s>\d{2})(?:\.(?P<ms>\d{3}))?')
    match = p.match(timecode_string)
    gd = match.groupdict(0)
    h, m, s, ms = [int(gd[x]) for x in ('h', 'm', 's', 'ms')]
    return 1000 * (h * 3600 + m * 60 + s) + ms


def get_timecode_from_time(time, include_ms=True):
    ms = time % 1000
    t = time // 1000
    s = t % 60
    t = t // 60
    m = t % 60
    h = t // 60
    if include_ms:
        return (h, m, s, ms)
    else:
        return (h, m, s)
