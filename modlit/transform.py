#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/27/18
"""
.. currentmodule:: modlit.transform
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Transforming data?  Look in here.
"""
from typing import Dict
from sqlalchemy import Column


class ModelMap(object):
    """
    A model map describes a set off alternate names that may be used to refer
    to a modeled object.
    """
    def __init__(self,
                 model_cls: type,
                 alt_tablename: str,
                 alt_columns: Dict[Column, str]):
        """

        :param model_cls: the ORM model class
        :param alt_tablename: the alternate table name
        :param alt_columns: a dictionary of alternate column names for column
            in a table
        """
        self._base_cls: type = model_cls
        self._alt_tablename: str = alt_tablename
        # The caller may have given us a dictionary with SQLAlchemy Columns
        # or strings as keys (maybe even a mixture of both).  So, we'll use
        # a dictionary comprehension to make sure that we end up with a
        # dictionary in which all the keys are column names (ie. strings).
        self._alt_columns: Dict[str, str] = (
            {
                key.name if isinstance(key, Column) else str(key): colname
                for (key, colname) in alt_columns
            }
            if alt_columns is not None
            else {}
        )

    @property
    def alt_tablename(self) -> str:
        """
        Get the mapped table name.

        :return: the mapped table name
        """
        return self._alt_tablename

    def get_alt_column(self, column: Column or str) -> str:
        """
        Get the mapped column name.

        :param column:
        :return:
        """
        key = column.name if isinstance(column, Column) else str(column)
        return self._alt_columns[key]

