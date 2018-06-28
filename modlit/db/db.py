#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 6/9/18
"""
.. currentmodule:: db
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Assets applicable to pretty much any database live in this module.
"""
# pylint: disable=protected-access
from functools import lru_cache
from typing import FrozenSet
from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnInfo(object):
    """
    This is a data object that describes a column in a database table.
    """
    column_name: str  #: the name of the column
    orm_type: type  #: the SQLAlchemy-compatible data type
    sql_type: str  #: the SQL type as stated by the database


@dataclass(frozen=True)
class GeometryColumnInfo(ColumnInfo):
    """
    This is a data object that extends :py:class:`ColumnInfo` to provide
    additional information about geometry columns.
    """
    coord_dimension: int  #: the number of geometry coordinate dimensions
    geometry_type: str  #: the SQLAlchemy-compatible data type
    srid: int  #: the spatial reference ID


@dataclass(frozen=True)
class TableInfo(object):
    """
    This is a named tuple that describes a table in a database.
    """
    schema: str  #: the schema in which the table resides
    table_name: str  #: the name of the table
    columns: FrozenSet[ColumnInfo]  #: the columns in the table

    @property
    @lru_cache()
    def geometry_column(self) -> GeometryColumnInfo or None:
        """
        Get the geometry column information (if the table has a geometry
        column, otherwise the property is `None`).

        :return: the geometry column information, or `None`
        """
        # Let's see if we have a geometry column.
        try:
            # If there is one, we should be able to find it in the list and
            # it should be a GeometryColumnInfo.
            return [
                gc for gc in self.columns
                if isinstance(gc, GeometryColumnInfo)
            ][0]
        except IndexError:
            return None
