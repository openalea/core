#!/usr/bin/env python
# -*- coding: utf-8 -*-

# {# pkglts, pysetup.kwds
# format setup arguments

from setuptools import setup, find_packages


short_descr = "OpenAlea.Core is able to discover and manage packages and logical components, build and evaluate dataflows and Generate final applications"
readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


def parse_requirements(fname):
    with open(fname, 'r') as f:
        txt = f.read()

    reqs = []
    for line in txt.splitlines():
        line = line.strip()
        if len(line) > 0 and not line.startswith("#"):
            reqs.append(line)

    return reqs

# find version number in src/openalea/core/version.py
version = {}
with open("src/openalea/core/version.py") as fp:
    exec(fp.read(), version)


setup_kwds = dict(
    name='openalea.core',
    version=version["__version__"],
    description=short_descr,
    long_description=readme + '\n\n' + history,
    author="openalea, Christophe Pradal, Samuel Dufour-Kowalski, revesansparole, ",
    author_email="openalea@inria.fr, christophe dot pradal at cirad dot fr, dufourko at cirad dot fr, revesansparole@gmail.com, ",
    url='https://github.com/openalea/core',
    license='cecill-c',
    zip_safe=False,

    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=parse_requirements("requirements.txt"),
    tests_require=parse_requirements("dvlpt_requirements.txt"),
    entry_points={},
    keywords='openalea',
    test_suite='nose.collector',
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
