#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/4/18
"""
.. currentmodule:: modlit.meta
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains metadata objects to help with inline documentation of the
model.
"""

from enum import IntFlag
from typing import Any, NamedTuple, Type, Union
from sqlalchemy import Column


COLUMN_META_ATTR = '__meta__'  #: the property that contains column metadata
TABLE_META_ATTR = '__meta__'  #: the property that contains table metadata


class Requirement(IntFlag):
    """
    This enumeration describes contracts with source data providers.
    """
    NONE = 0  #: data for the column is neither requested nor required
    REQUESTED = 1  #: data for the column is requested
    REQUIRED = 3  #: data for the column is required


class Source(NamedTuple):
    """
    'Source' information defines contracts with data providers.

    :ivar requirement:  defines the source data contract
    :vartype requirement: :py:class:`Requirement`
    """
    requirement: Requirement = Requirement.NONE


class Usage(IntFlag):
    """
    This enumeration describes how data may be used.
    """
    NONE = 0  #: The data is not used.
    SEARCH = 1  #: The data is used for searching.
    DISPLAY = 2  #: The data is displayed to users.


class Target(NamedTuple):
    """
    'Target' information describes contracts with data consumers.

    :ivar usage:  defines how the data in the column is expected to be used
    :vartype usage: :py:class:`Usage`
    :ivar guaranteed:  Is the column guaranteed to contain a non-empty value?
    :vartype guaranteed: bool
    :ivar calculated:  May the column's value be generated or modified by
        a calculation?
    :vartype calculated: bool
    """
    usage: Usage = Usage.NONE
    guaranteed: bool = False
    calculated: bool = False


class TableMeta(NamedTuple):
    """
    Metadata for tables.

    :ivar label: a human-friendly label for the column
    :vartype label: `str`
    """
    label: str = None  #: a human-friendly label for the column


class ColumnMeta(NamedTuple):
    """
    Metadata for table columns.

    :ivar label: a human-friendly label for the column
    :vartype label: str
    :ivar description:  a human-friendly description of the column
    :vartype description: str
    :ivar nena:  the name of the equivalent NENA field
    :vartype nena: str
    """
    label: str = None
    description: str = 'This field needs a description.'
    nena: str or None = None
    source: Source = Source()
    target: Target = Target()

    def get_enum(
            self,
            enum_cls: Type[Union[Requirement, Usage]]
    ) -> Requirement or Usage or None:
        """
        Get the current value of an attribute defined by an enumeration.

        :param enum_cls: the enumeration class
        :return: the value of the attribute
        """
        if enum_cls == Requirement:
            return self.source.requirement
        elif enum_cls == Usage:
            return self.target.usage
        return None


def column(dtype: Any, meta: ColumnMeta, *args, **kwargs) -> Column:
    """
    Create a GeoAlchemy :py:class:`Column` annotated with metadata.

    :param dtype: the GeoAlchemy column type
    :param meta: the meta data
    :return: a GeoAlchemy :py:class:`Column`
    """
    col = Column(dtype, *args, **kwargs)
    col.__dict__[COLUMN_META_ATTR] = meta
    return col
