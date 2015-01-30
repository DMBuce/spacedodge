#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='lineyspace',
    version='0.1',
    description='Liney Space',
    author='Nate Woodward',
    author_email='nate.lineyspace@natewoodward.org',
    #url=''
    packages=['lineyspace'],
    package_data={'lineyspace': ['data/*.png']}
)

