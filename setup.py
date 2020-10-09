#!/usr/bin/env python
# -*- coding: utf-8 -*-

# {# pkglts, pysetup.kwds
# format setup arguments

from setuptools import setup, find_packages
from io import open


short_descr = "OpenAlea.Core is able to discover and manage packages and logical components, build and evaluate dataflows and Generate final applications"
readme = open('README.rst').read()
history = open('HISTORY.rst').read()


# find version number in src/openalea/core/version.py
version = {}
with open("src/openalea/core/version.py") as fp:
    exec(fp.read(), version)

# find packages
pkgs = find_packages('src')



setup_kwds = dict(
    name='openalea.core',
    version=version["__version__"],
    description=short_descr,
    long_description=readme + '\n\n' + history,
    author="Christophe Pradal",
    author_email="christophe dot pradal at cirad dot fr",
    url='https://github.com/openalea/core',
    license='cecill-c',
    zip_safe=False,

    packages=pkgs,
    namespace_packages=['openalea'],
    package_dir={'': 'src'},
    setup_requires=[
        "pytest-runner",
        ],
    install_requires=[
        ],
    tests_require=[
        "coverage",
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "sphinx",
        ],
    entry_points={},
    keywords='openalea',
    )
# #}
# change setup_kwds below before the next pkglts tag

setup_kwds['setup_requires'] = ['openalea.deploy']
setup_kwds['share_dirs'] = {'share': 'share'}
setup_kwds['entry_points']["wralea"] = ["openalea.flow control = openalea.core.system", ]
setup_kwds['entry_points']["console_scripts"] = ["alea = openalea.core.alea:main"]
setup_kwds['entry_points']['openalea.core'] = [
            'openalea.core/openalea = openalea.core.plugin.builtin',
        ]

# do not change things below
# {# pkglts, pysetup.call
setup(**setup_kwds)
# #}
