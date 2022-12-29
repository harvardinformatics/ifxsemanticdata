# -*- coding: utf-8 -*-

'''
setup for ifxsemanticdata

Created on  2020-04-30

@author: Meghan Correa <mportermahoeny@g.harvard.edu>
@copyright: 2020 The Presidents and Fellows of Harvard College. All rights reserved.
@license: GPL v2.0
'''

import re
from setuptools import setup, find_packages


def getVersion():
    """
    Retrieve the version number from the __init__ file
    """
    version = '0.0.0'
    with open('ifxsemanticdata/__init__.py', 'r') as f:
        contents = f.read().strip()

    m = re.search(r"__version__ = '([\d\.]+)'", contents)
    if m:
        version = m.group(1)
    return version


setup(
    name="ifxsemanticdata",
    version=getVersion(),
    author='Meghan Correa <mportermahoney@g.harvard.edu>',
    author_email='mportermahoney@g.harvard.edu',
    description='Semantic data migration for Informatics applications',
    license='LICENSE',
    include_package_data=True,
    url='https://github.com/harvardinformatics/ifxsemanticdata',
    packages=find_packages(),
    long_description='Semantic data migration for Informatics applications',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
    install_requires = [
        'Django>3, <4',
        'ifxurls',
        'requests',
        'djangorestframework>3.8'
    ],
    dependency_links = [
        'git+https://github.com/harvardinformatics/ifxurls.git'
    ]
)
