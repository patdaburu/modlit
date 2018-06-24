#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 6/9/18
"""
.. currentmodule:: db
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Assets applicable to pretty much any database live in this module.
"""
from typing import Iterable, NamedTuple


class ColumnInfo(object):
    """
    This is a data object that describes a column in a database table.
    """

    def __init__(self,
                 column_name: str,
                 orm_type: str,
                 sql_type: str):
        self.column_name: str = column_name  #: the name of the column
        self.orm_type: type = orm_type  #: the SQLAlchemy-compatible data type
        self.sql_type: str = sql_type  #: the SQL type as stated by the database


# pylint: disable=too-many-arguments
class GeometryColumnInfo(ColumnInfo):
    """
    This is a data object that extends :py:class:`ColumnInfo` to provide
    additional information about geometry columns.
    """
    def __init__(self,
                 column_name: str,
                 orm_type: str,
                 sql_type: str,
                 coord_dimension: int,
                 geometry_type: str,
                 srid: int):
        super().__init__(column_name=column_name,
                         orm_type=orm_type,
                         sql_type=sql_type)
        self.coord_dimension: int = coord_dimension  #: the coordinate dimensions
        self.geometry_type: str = geometry_type #: the SQLAlchemy geometry type name
        self.srid: int = srid #: the spatial reference ID


class TableInfo(NamedTuple):
    """
    This is a named tuple that describes a table in a database.
    """
    schema: str  #: the schema in which the table resides
    table_name: str  #: the name of the table
    columns: Iterable[ColumnInfo]  #: the columns in the table
