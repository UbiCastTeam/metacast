#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imp
from distutils.core import setup

metacast = imp.load_source('metacast', 'metacast/__init__.py')

setup(
    name='metacast',
    version=metacast.__version__,
    description='Rich media metadata handling library.',
    author='UbiCast',
    author_email='support@ubicast.eu',
    url='https://github.com/UbiCastTeam/metacast',
    license='GNU LGPL v2.1',
    packages=['metacast'],
    scripts=['scripts/metacast_timeshift'],
    install_requires=['lxml'],
)
