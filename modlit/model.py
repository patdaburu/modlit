#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/5/18
"""
.. currentmodule:: modlit.model
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains general members to help you work with the model.
"""
import inspect
from typing import List
from .meta import Column, COLUMN_META_ATTR, TableMeta, TABLE_META_ATTR
from .modules import walk_load


IS_MODEL_CLASS = '__model_cls__'  #: signifies a model class


def model(label: str):
    """
    Use this decorator to provide meta-data for your model class.

    :param label: the friendly label for the class
    """

    def modelify(cls):
        """
        This inner function updates the model class.

        :param cls: the decorated class
        :return: the original class
        """
        # In all cases, flag the class as a 'model' class.
        setattr(cls, IS_MODEL_CLASS, True)
        # If the label parameter hasn't already been specified...
        if not hasattr(cls, TABLE_META_ATTR):
            # ...update it now.
            setattr(cls, TABLE_META_ATTR, TableMeta(label=label))

        # Let's go through every class in the hierarchy...
        for mro in inspect.getmro(cls):
            for name, obj in inspect.getmembers(mro):
                # If this attribute:
                #   1) has the same name as an attribute of the current class;
                #   2) is a Column; and
                #   3) has a 'meta' attribute...
                if (hasattr(cls, name) and
                        isinstance(obj, Column) and
                        hasattr(obj, COLUMN_META_ATTR)):
                    # ...we need to take a closer look at it.
                    column: Column = getattr(cls, name)
                    # If this class' own attribute is missing the 'meta'
                    # information...
                    if not hasattr(column, COLUMN_META_ATTR):
                        # ...copy it from the parent class.
                        setattr(column,
                                COLUMN_META_ATTR,
                                getattr(obj, COLUMN_META_ATTR))
        # Return the original class.
        return cls

    # Return the inner function.
    return modelify


def load(package, skip_modules: List[str] = None):
    """
    Load the data model.

    :param package: the package that contains the model classes
    :param skip_modules: a list of names of the modules that should be skipped
        when importing the package
    """
    walk_load(package, skip_modules=skip_modules)
