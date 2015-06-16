#! /usr/bin/env python

""" j2cli main file """
from __future__ import unicode_literals
import pkg_resources

__author__ = "Mark Vartanyan"
__email__ = "kolypto@gmail.com"
__version__ = pkg_resources.get_distribution('j2cli').version

from j2cli.cli import main

if __name__ == '__main__':
    main()
