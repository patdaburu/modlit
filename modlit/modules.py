#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/6/18
"""
.. currentmodule:: modlit.modules
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Sometimes we need to do things like loading modules dynamically.  The tools
to help with that are in here.
"""
import pkgutil
from typing import List


def walk_load(package, skip_modules: List[str] = None):
    """
    Walk and load the modules in a package.

    :param package: the package that contains the model classes
    :param skip_modules: a list of names of the modules that should be skipped
        when importing the package
    """
    # Get the package's name...
    prefix = package.__name__ + '.'
    # ...so that we may import all its modules, one-by-one!
    for _, modname, _ in pkgutil.walk_packages(
            package.__path__, prefix):
        # If a module is explicitly excluded by name...
        if skip_modules and modname in skip_modules:
            # ...skip it.
            continue
        else:
            # Otherwise, load it up!
            _ = __import__(modname)
