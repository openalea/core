#!/usr/bin/env python
# -*- coding: utf-8 -*-

# format setup arguments

from setuptools import setup, find_packages
from io import open


short_descr = "OpenAlea.Core is able to discover and manage packages and logical components, build and evaluate dataflows and generate final applications"
readme = open('README.rst').read()
history = open('HISTORY.rst').read()


# find version number in src/openalea/core/version.py
_version = {}
with open("src/openalea/core/version.py") as fp:
    exec(fp.read(), _version)
    version = _version["__version__"]

# find packages
pkgs = find_packages('src')

setup_kwds = dict(
    name='openalea.core',
    version=version,
    description=short_descr,
    long_description=readme + '\n\n' + history,
    author="Christophe Pradal",
    author_email="christophe dot pradal at cirad dot fr",
    url='https://github.com/openalea/core',
    license='cecill-c',
    zip_safe=False,

    packages=pkgs,
    #namespace_packages=['openalea'],
    package_dir={'': 'src'},
    entry_points={},
    keywords='openalea',
    )

setup_kwds['setup_requires'] = ['openalea.deploy']
setup_kwds['share_dirs'] = {'share': 'share'}
setup_kwds['entry_points']["wralea"] = ["openalea.flow control = openalea.core.system", ]
setup_kwds['entry_points']["console_scripts"] = ["alea = openalea.core.alea:main"]
setup_kwds['entry_points']['openalea.core'] = [
            'openalea.core/openalea = openalea.core.plugin.builtin',
        ]

setup(**setup_kwds)
