#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Support and Resistance Trendlines Calculator for Financial Analysis
# https://github.com/GregoryMorse/trendln

"""Support and Resistance Trendlines Calculator for Financial Analysis"""

#pip install twine

#cd /D D:\OneDrive\Documents\Projects\trader\trendln
#python setup.py sdist
#twine upload dist/*
#pip install trendln --upgrade

from setuptools import setup, find_packages
import io
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with io.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='trendln',
    version="0.1",
    description='Support and Resistance Trendlines Calculator',
    long_description=long_description,
    url='https://github.com/GregoryMorse/trendln',
    author='Gregory Morse',
    author_email='gregory.morse@live.com',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',


        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    platforms = ['any'],
    keywords='trendlines, trend lines, trend, support, resistance, trends, technical, indicators, financial, analysis',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'examples']),
    install_requires=['pandas>=0.24', 'numpy>=1.15'],
    entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },
)
