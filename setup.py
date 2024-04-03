#!/usr/bin/env python
""" j2cli - Jinja2 Command-Line Tool
================================

`j2cli` is a command-line tool for templating in shell-scripts,
leveraging the [Jinja2](http://jinja.pocoo.org/docs/) library.

Features:

* Jinja2 templating
* INI, YAML, JSON data sources supported
* Allows the use of environment variables in templates! Hello [Docker](http://www.docker.com/) :)

Inspired by [mattrobenolt/jinja2-cli](https://github.com/mattrobenolt/jinja2-cli)
"""

from setuptools import setup, find_packages
import sys

# PyYAML 3.11 was the last to support Python 2.6
# This code limits pyyaml version for older pythons
pyyaml_version = 'pyyaml >= 3.10'  # fresh
if sys.version_info[:2] == (2, 6):
    pyyaml_version = 'pyyaml<=3.11'


setup(
    name='j2cli',
    version='0.3.12b',
    author='Mark Vartanyan',
    author_email='kolypto@gmail.com',

    url='https://github.com/kolypto/j2cli',
    license='BSD',
    description='Command-line interface to Jinja2 for templating in shell scripts.',
    long_description=__doc__,  # can't do open('README.md').read() because we're describing self
    long_description_content_type='text/markdown',
    keywords=['Jinja2', 'templating', 'command-line', 'CLI'],

    packages=find_packages(),
    scripts=[],
    entry_points={
        'console_scripts': [
            'j2 = j2cli:main',
        ]
    },

    install_requires=[
        'jinja2 >= 2.7.2',
        'six >= 1.10',
    ],
    extras_require={
        'yaml': [pyyaml_version,]
    },
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',

    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
