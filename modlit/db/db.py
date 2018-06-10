#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 6/9/18
"""
.. currentmodule:: db
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Assets applicable to pretty much any database live in this module.
"""
from typing import Iterable, NamedTuple


class ColumnInfo(NamedTuple):
    """
    This is a named tuple that describes a column in a database table.
    """
    column_name: str  #: the name of the column
    orm_type: type  #: the SQLAlchemy-compatible data type


class TableInfo(NamedTuple):
    """
    This is a named tuple that describes a table in a database.
    """
    schema: str  #: the schema in which the table resides
    table_name: str  #: the name of the table
    columns: Iterable[ColumnInfo]  #: the columns in the table
