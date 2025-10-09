#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

import metacast

setup(
    name='metacast',
    version=metacast.__version__,
    description='Rich media metadata handling library.',
    author='UbiCast',
    author_email='support@ubicast.eu',
    url='https://github.com/UbiCastTeam/metacast',
    license='GNU LGPL v2.1',
    packages=['metacast'],
    install_requires=['lxml'],
)
