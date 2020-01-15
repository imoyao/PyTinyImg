#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Administrator at 2020/1/15 23:24
from setuptools import setup, find_packages
import settings
setup(
    name=settings.NAME,
    version=settings.VERSION,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'tinify',
    ],
    entry_points='''
        [console_scripts]
        yst=PyTinyImg.scripts.yst:cli
    ''',
)