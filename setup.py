#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

here = lambda *a: os.path.join(os.path.dirname(__file__), *a)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

#readme = open(here('README.md')).read()
requirements = [x.strip() for x in open(here('requirements.txt')).readlines()]

setup(
    name='nadamp',
    version='0.1.0',
    description='',
    author='Bennett Kanuka',
    author_email='bkanuka@gmail.com',
    url='https://github.com/bkanuka/nadamp',
    py_modules=['nadamp'],
    include_package_data=True,
    scripts=['ampcontrol'],
)
