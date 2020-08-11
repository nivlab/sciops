#! /usr/bin/env python
#
# Copyright (c) 2020 Niv Lab
# https://nivlab.princeton.edu/

import os, sys
from setuptools import setup, find_packages
path = os.path.abspath(os.path.dirname(__file__))

## Metadata
DISTNAME = 'laverna'
MAINTAINER = 'Sam Zorowitz'
MAINTAINER_EMAIL = 'zorowitz@princeton.edu'
DESCRIPTION = 'Code for simulating low-effort behavior'
URL = 'https://github.com/nivlab/silver-screen'
LICENSE = 'MIT'
DOWNLOAD_URL = 'https://github.com/nivlab/silver-screen'

with open(os.path.join(path, 'README.md'), encoding='utf-8') as readme_file:
    README = readme_file.read()

with open(os.path.join(path, 'requirements.txt')) as requirements_file:
    # Parse requirements.txt, ignoring any commented-out lines.
    requirements = [line for line in requirements_file.read().splitlines()
                    if not line.startswith('#')]
    
VERSION = None
with open(os.path.join('laverna', '__init__.py'), 'r') as fid:
    for line in (line.strip() for line in fid):
        if line.startswith('__version__'):
            VERSION = line.split('=')[1].strip().strip('\'')
            break
if VERSION is None:
    raise RuntimeError('Could not determine version')

setup(name=DISTNAME,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      description=DESCRIPTION,
      url=URL,
      version=VERSION,
      download_url=DOWNLOAD_URL,
      long_description=README,
      packages=find_packages(exclude=['docs', 'tests']),
      install_requires=requirements,
      license=LICENSE
)