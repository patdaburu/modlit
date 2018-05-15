#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/4/18
"""
.. currentmodule:: modlit.meta
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains metadata objects to help with inline documentation of the
model.
"""
from abc import ABC
from enum import IntFlag
import re
from functools import reduce
from typing import Any, Type, Union
from typing import cast, Iterable
from orderedset import OrderedSet
from sqlalchemy import Column


COLUMN_META_ATTR = '__meta__'  #: the property that contains column metadata
TABLE_META_ATTR = '__meta__'  #: the property that contains table metadata


class _MetaDescription(ABC):
    """
    This is base class for objects that provide meta-data descriptions.
    """

    def __eq__(self, other):
        try:
            # Compare the values in all the slots.
            for slot in self.__slots__:
                # If one of the values isn't equal...
                if getattr(self, slot) != getattr(other, slot):
                    # ...the objects aren't equal.
                    return False
            # It looks like everything was the same.  Great.
            return True
        except AttributeError:
            # This may happen if the object's aren't of the same type (or
            # at least they don't quack alike).  If it does, let the parent
            # class take over.
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        # We will establish the parameter names by removing the underscore from
        # the names we find in the __slots__, but we'll get the values according
        # to (of course) the original names we find.  This is in accordance
        # with a convention shared by the classes in this module that inherit
        # from this object to gain common behavior.
        params = [
            f'{slot}={repr(getattr(self, slot))[1:]}'
            for slot in getattr(self, '__slots__')
        ]
        # Now put it all together with the class name to produce a
        # pseudo-constructor string.
        return f"{self.__class__.__name__}({', '.join(params)})"


class _Synonyms(object):
    """
    This is a helper object that keeps track of synonyms for meta-info objects.
    """
    __slots__ = ['_synonyms', '_synonyms_re']

    def __init__(self, synonyms: Iterable[str] = None):
        """

        :param synonyms: the synonyms
        """
        self._synonyms: OrderedSet[str] = (
            OrderedSet(synonyms) if synonyms is not None
            else set()
        )
        # Create a set of regular-expression objects we can use to determine
        # if a given string is a synonym for this source column's name.
        self._synonyms_re: OrderedSet = OrderedSet(
            [re.compile(s, re.IGNORECASE) for s in self._synonyms]
        )

    def is_synonym(self, name: str):
        """
        Is a given name a synonym for an item in the set?

        :param name: the name to test
        :return: `True` if the name appears to be a synonym, otherwise `False`
        """
        # Evaluate each of the synonym regular expressions.
        for synonym_re in self._synonyms_re:
            # If we find that this one matches the name...
            if synonym_re.match(name):
                # ...the name is a synonym.
                return True
        # If we didn't return before it means we didn't find any matches, so...
        return False

    def __eq__(self, other):
        try:
            return self._synonyms == getattr(other, '_synonyms')
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Requirement(IntFlag):
    """
    This enumeration describes contracts with source data providers.
    """
    NONE = 0  #: data for the column is neither requested nor required
    REQUESTED = 1  #: data for the column is requested
    REQUIRED = 3  #: data for the column is required


class Source(_MetaDescription):
    """
    'Source' information defines contracts with data providers.
    """
    __slots__ = ['_requirement', '_synonyms']

    def __init__(self,
                 requirement: Requirement = Requirement.NONE,
                 synonyms: Iterable[str] = None):
        """

        :param requirement: the source contract
        :param synonyms: name patterns that may indicate
        """
        self._requirement: Requirement = requirement
        self._synonyms = _Synonyms(synonyms)

    @property
    def requirement(self) -> Requirement:
        """
        Get the source data contract.

        :return: the source data contract
        """
        return self._requirement

    def is_synonym(self, name: str):
        """
        Is a given name a synonym for this source column?

        :param name: the name to test
        :return: `True` if the name appears to be a synonym, otherwise `False`
        """
        return self._synonyms.is_synonym(name)


class Usage(IntFlag):
    """
    This enumeration describes how data may be used.
    """
    NONE = 0  #: The data is not used.
    SEARCH = 1  #: The data is used for searching.
    DISPLAY = 2  #: The data is displayed to users.


class Target(_MetaDescription):
    """
    'Target' information describes contracts with data consumers.
    """
    __slots__ = ['_guaranteed', '_calculated', '_usage']

    def __init__(self,
                 guaranteed: bool = False,
                 calculated: bool = False,
                 usage: Usage or Iterable[Usage] = Usage.NONE):
        self._guaranteed = guaranteed
        self._calculated = calculated
        # Let's start by assuming we were passed a simple value for `usage`.
        _usage = usage
        # But we may have been provided an iteration of values that we need
        # to combine, so...
        try:
            # ...we need to see if we can iterate the argument.  If we can,
            # we'll get a logical OR of all the values.
            _usage = reduce(lambda a, b: a | b, cast(Iterable, usage))
        except TypeError:
            pass  # The argument wasn't iterable.
        self._usage = _usage

    @property
    def guaranteed(self) -> bool:
        """
        Is the column guaranteed to contain a non-empty value?

        :return: `True` if the column is guaranteed to contain a non-empty
            value, otherwise `False`
        """
        return self._guaranteed

    @property
    def calculated(self) -> bool:
        """
        May the column's value be generated or modified by a calculation?

        :return: `True` if the column may be generated or modified by a
            calculation, otherwise `False`
        """
        return self._calculated

    @property
    def usage(self) -> Usage:
        """
        Get the :py:class:`Usage` flag for the column.

        :return: a single flag value that indicates the ways in which the
            data in this column is expected to be used
        """
        return self._usage


class TableMeta(_MetaDescription):
    """
    Metadata for tables.
    """
    __slots__ = ['_label', '_synonyms']

    def __init__(self,
                 label: str = None,
                 synonyms: Iterable[str] = None):
        """

        :param label: the human-friendly label for the column
        """
        self._label = label
        self._synonyms = _Synonyms(synonyms)

    @property
    def label(self) -> str:
        """
        Get the human-friendly label for the column.

        :return: the human-friendly label
        """
        return self._label


class ColumnMeta(_MetaDescription):
    """
    Metadata for table columns.
    """
    __slots__ = ['_label', '_description', '_nena', '_source', '_target']

    def __init__(self,
                 label: str = None,
                 description: str = None,
                 nena: str = None,
                 source: Source = None,
                 target: Target = None):
        self._label = label if label is not None else ''
        self._description = description if description is not None else ''
        self._nena = nena
        self._source = source if source is not None else Source()
        self._target = target if target is not None else Target()

    @property
    def label(self) -> str:
        """
        Get the human-friendly label for the column.

        :return: the human-friendly label for the column
        """
        return self._label

    @property
    def description(self) -> str:
        """
        Get the human-friendly description of the column.

        :return: the human-friendly description of the column
        """
        return self._description

    @property
    def nena(self) -> str:
        """
        Get the name of the `NENA <https://www.nena.org/>`_ equivalent field.

        :return: the `NENA <https://www.nena.org/>`_ equivalent field.
        """
        return self._nena

    @property
    def source(self) -> Source:
        """
        Get the information about the source data contract.

        :return: the source data contract
        """
        return self._source

    @property
    def target(self) -> Target:
        """
        Get the information for the target data contract.

        :return: the target data contract
        """
        return self._target

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
            return self._source.requirement
        elif enum_cls == Usage:
            return self._target.usage
        return None


def column(dtype: Any, meta: ColumnMeta, *args, **kwargs) -> Column:
    """
    Create a GeoAlchemy :py:class:`Column` annotated with metadata.

    :param dtype: the SQLAlchemy/GeoAlchemy column type
    :param meta: the meta data
    :return: a GeoAlchemy :py:class:`Column`
    """
    col = Column(dtype, *args, **kwargs)
    col.__dict__[COLUMN_META_ATTR] = meta
    return col
