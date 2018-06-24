#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 6/9/18
"""
.. currentmodule:: db
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Assets applicable to pretty much any database live in this module.
"""
# pylint: disable=protected-access
from typing import Iterable, List


class ColumnInfo(object):
    """
    This is a data object that describes a column in a database table.
    """
    # FUTURE: This would probably be a great use of dataclasses in 3.7!!

    __slots__ = ['_column_name', '_orm_type', '_sql_type', '_comparator']

    def __init__(self,
                 column_name: str,
                 orm_type: type,
                 sql_type: str):
        """

        :param column_name: the name of the column
        :param orm_type: the SQLAlchemy-compatible data type
        :param sql_type: the SQL type as stated by the database
        """
        self._column_name: str = column_name
        self._orm_type: type = orm_type
        self._sql_type: str = sql_type
        # Create a comparator tuple for easier equality testing later on.
        self._comparator = tuple([
            getattr(self, slot) for slot in self.__slots__
            if slot != '_comparator'
        ])

    @property
    def column_name(self) -> str:
        """
        Get the name of the column.

        :return: the name of the column
        """
        return self._column_name

    @property
    def orm_type(self) -> type:
        """
        Get the SQLAlchemy-compatible data type.

        :return: the SQLAlchemy-compatible data type
        """
        return self._orm_type

    @property
    def sql_type(self) -> str:
        """
        Get the SQL data type.

        :return: the SQL data type
        """
        return self._sql_type

    def __eq__(self, other: 'ColumnInfo'):
        return self._comparator == other._comparator if other else None

    def __ne__(self, other: 'ColumnInfo'):
        return not self.__eq__(other)


# pylint: disable=too-many-arguments
class GeometryColumnInfo(ColumnInfo):
    """
    This is a data object that extends :py:class:`ColumnInfo` to provide
    additional information about geometry columns.
    """
    # FUTURE: This would probably be a great use of dataclasses in 3.7!!

    __slots__ = [
        '_column_name', '_orm_type', '_sql_type',
        '_coord_dimension', '_geometry_type', '_srid',
        '_comparator'
    ]

    def __init__(self,
                 column_name: str,
                 orm_type: type,
                 sql_type: str,
                 coord_dimension: int,
                 geometry_type: str,
                 srid: int):
        """

        :param column_name: the name of the column
        :param orm_type: the SQLAlchemy-compatible data type
        :param sql_type: the SQL type as stated by the database
        :param coord_dimension: the geometry coordinate dimensions
        :param geometry_type: the PostGIS geometry type as state by the database
        :param srid: the spatial reference ID (SRID)
        """
        # We need to set the basic properties before we call the parent
        # constructor to assist with the construction of the comparator.
        self._coord_dimension: int = coord_dimension
        self._geometry_type: str = geometry_type
        self._srid: int = srid
        super().__init__(column_name=column_name,
                         orm_type=orm_type,
                         sql_type=sql_type)

    @property
    def coord_dimension(self) -> int:
        """
        Get the number of dimensions supported by the coordinate geometry

        :return: the number of dimensions supported by the coordinate geometry
        """
        return self._coord_dimension

    @property
    def geometry_type(self) -> str:
        """
        Get the PostGIS geometry type as stated by the database.

        :return: the PostGIS geometry as stated by the database
        """
        return self._geometry_type

    @property
    def srid(self) -> int:
        """
        Get the spatial reference ID (SRID) geometry.

        :return: the spatial reference ID of the geometry
        """
        return self._srid


class TableInfo(object):
    """
    This is a named tuple that describes a table in a database.
    """
    # schema: str  #: the schema in which the table resides
    # table_name: str  #: the name of the table
    # columns: Iterable[ColumnInfo]  #: the columns in the table

    __slots__ = [
        '_schema', '_table_name', '_columns', '_geometry_column',
        '_comparator'
    ]

    def __init__(self,
                 schema: str,
                 table_name: str,
                 columns: Iterable[ColumnInfo]):
        """

        :param schema: the schema in which the table resides
        :param table_name: the name of the table
        :param columns: the columns in the table
        """
        self._schema = schema
        self._table_name = table_name
        self._columns: List[ColumnInfo] = list(columns)
        # Let's see if we have a geometry column.
        try:
            # If there is one, we should be able to find it in the list and
            # it should be a GeometryColumnInfo.
            self._geometry_column = [
                gc for gc in self._columns
                if isinstance(gc, GeometryColumnInfo)
            ][0]
        except IndexError:
            self._geometry_column = None  # There was no geometry column.
        # Create a comparator tuple for easier equality testing later on.
        self._comparator = tuple([
            getattr(self, slot) for slot in self.__slots__
            if slot != '_comparator'
        ])

    @property
    def schema(self) -> str:
        """
        Get the schema in which the table resides.

        :return: the schema in which the table resides
        """
        return self._schema

    @property
    def table_name(self) -> str:
        """
        Get the name of the table.

        :return: the name of the table
        """
        return self._table_name

    @property
    def columns(self) -> Iterable[ColumnInfo]:
        """
        Get the table's column information.

        :return: the table's columns
        """
        return self._columns

    @property
    def geometry_column(self) -> GeometryColumnInfo or None:
        """
        Get the geometry column information (if the table has a geometry
        column, otherwise the property is `None`).

        :return: the geometry column information, or `None`
        """
        return self._geometry_column

    def __eq__(self, other: 'TableInfo'):
        return self._comparator == other._comparator if other else None

    def __ne__(self, other: 'TableInfo'):
        return not self.__eq__(other)
