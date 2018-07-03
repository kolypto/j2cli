#!/usr/bin/env python
"""
shinto-cli
==========

Command-line interface to [Jinja2](http://jinja.pocoo.org/docs/) for templating in shell scripts.

Features:

* Jinja2 templating
* Allows to use environment variables! Hello [Docker](http://www.docker.com/) :)
* INI, YAML, JSON data sources supported

Inspired by [mattrobenolt/jinja2-cli](https://github.com/mattrobenolt/jinja2-cli)
Inspired by [kolypto/jinja2-cli](https://github.com/kolypto/j2cli)
"""

from setuptools import setup, find_packages

setup(
    name='shinto-cli',
    version='0.5.0-0',
    author='ISL',
    author_email='dev@isl.co',

    url='https://github.com/istrategylabs/shinto-cli',
    license='BSD',
    description='Command-line interface to Jinja2 for templating in shell scripts.',
    long_description=__doc__,
    long_description_content_type='text/markdown',
    keywords=['Jinja2', 'templating', 'command-line', 'CLI'],

    packages=find_packages(),
    scripts=[],
    entry_points={
        'console_scripts': [
            'j2 = shinto_cli:main',
        ]
    },

    install_requires=[
        'jinja2 >= 2.7.2',
    ],
    extras_require={
        'yaml': ['pyyaml', ]
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
        #'Programming Language :: Python :: 3',
    ],
)
