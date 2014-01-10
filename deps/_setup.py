#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
Stocks monitor setup script
Automatically pull app dependencies and install/update them
"""

from setuptools import setup
import os

os.chdir(os.path.join(os.path.dirname(__file__), '../tmp/eggs/'))


setup(
    name='stocks-monitor',
    version='0.1.0',
    description='Live Stocks Monitor Screen',
    url='https://code.frenchtouch.pro/enib/stocks-monitor',

    author=u'Valérian Saliou',
    author_email='valerian@valeriansaliou.name',

    install_requires=[
        'requests==2.2.0',
        'websocket-client==0.12.0',
        'raspberry-pi-lcd==1.1.1',
    ]
)
