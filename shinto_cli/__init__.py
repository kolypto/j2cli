#! /usr/bin/env python

""" shinto_cli main file """
import pkg_resources

__author__ = "ISL"
__email__ = "dev@isl.co"
__version__ = pkg_resources.get_distribution('shinto-cli').version

from shinto_cli.cli import main

if __name__ == '__main__':
    main()
