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
from typing import cast, Any, Iterable, Type, Union
from orderedset import OrderedSet
from sqlalchemy import Column
from sqlalchemy.orm.attributes import InstrumentedAttribute
from .errors import ModlitError


COLUMN_META_ATTR = '__meta__'  #: the property that contains column metadata
TABLE_META_ATTR = '__meta__'  #: the property that contains table metadata


class ConstraintException(ModlitError):
    """
    Raised when errors pertaining to constraints are encountered.

    ..seealso::

        :py:class:`Constraint`
    """
    pass


class DuplicateConstraintException(ConstraintException):
    """
    Raised when duplicate, potentially conflicting constraints are encountered.

    ..seealso::

        :py:class:`Constraint`
    """


# class InvalidConstraintException(ConstraintException):
#     """
#     Raised when a constraint is applied to an inappropriate type.
#
#     ..seealso::
#
#         :py:class:`Constraint`
#     """


class _MetaDescription(ABC):
    """
    This is base class for objects that provide meta-data descriptions.
    """
    pass


class _Synonyms(object):
    """
    This is a helper object that keeps track of synonyms for meta-info objects.
    """

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

    @property
    def synonyms(self) -> Iterable[str]:
        """
        Get the synonymous names.

        :return: an iteration of the synonymous names
        """
        return iter(self._synonyms)

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


class _HasSynonyms(object):
    """
    Mix this into your meta object if the meta information describes a named
    object with synonyms.
    """
    def __init__(self,
                 synonyms: Iterable[str],
                 *args, **kwargs):
        """

        :param synonyms: the synonyms
        """
        super().__init__(*args, **kwargs)  # cooperative super()
        self._synonyms = _Synonyms(synonyms)

    @property
    def synonyms(self) -> Iterable[str]:
        """
        Get the synonymous names for this table.

        :return: an iteration of the synonymous names
        """
        return self._synonyms.synonyms

    def is_synonym(self, name: str) -> bool:
        """
        Test a name to see if it's a synonym for the table's name.

        :param name: the table name
        :return: `True` if the name is a synonym for this table, otherwise
            `False`
        """
        return self._synonyms.is_synonym(name)


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

    def __init__(self,
                 requirement: Requirement = Requirement.NONE,
                 synonyms: Iterable[str] = None):
        """

        :param requirement: the source contract
        :param synonyms: name patterns that may be used to detect this source
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


class ModelMeta(_MetaDescription):
    """
    Metadata for entire data models.
    """

    def __init__(self,
                 title: str,
                 slug: str,
                 author_name: str,
                 author_email: str,
                 version: str):
        """

        :param title: a friendly, human-readable title for the model
        :param slug: a short identifier for the model
        :param author_name: the name of the model's author
        :param author_email: the model author's email address
        :param version:
        """
        self._title = title
        self._slug = slug
        self._author_name = author_name
        self._author_email = author_email
        self._version = version

    def get_urn(self) -> str:
        """
        Get the uniform resource name (URN) that identifies the model.
        """
        return f'urn:com.geo-comm.modlit:{self._slug}:{self._version}'

    @property
    def title(self) -> str:
        """
        Get the model's friendly, descriptive, human-readable title.
        """
        return self._title

    @property
    def author_name(self) -> str:
        """
        Get the model author's name.
        """
        return self._author_name

    @property
    def author_email(self) -> str:
        """
        Get the model author's email.
        """
        return self._author_name

    @property
    def version(self) -> str:
        """
        Get the model version.
        """
        return self._version


class TableMeta(_MetaDescription, _HasSynonyms):
    """
    Metadata for tables.
    """
    def __init__(self,
                 label: str = None,
                 synonyms: Iterable[str] = None):
        """

        :param label: the human-friendly label for the column
        """
        super().__init__(synonyms=synonyms)
        self._label = label

    @property
    def label(self) -> str:
        """
        Get the human-friendly label for the column.

        :return: the human-friendly label
        """
        return self._label


class ColumnMeta(_MetaDescription, _HasSynonyms):
    """
    Metadata for table columns.
    """

    def __init__(self,
                 label: str = None,
                 description: str = None,
                 nena: str = None,
                 source: Source = None,
                 target: Target = None,
                 synonyms: Iterable[str] = None):
        super().__init__(synonyms=synonyms)
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
        if enum_cls == Usage:
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


def get_table_meta(model) -> TableMeta or None:
    """
    Retrieve the table metadata for from a model (ORM) object.

    :param model: the model (ORM) object
    :return: the table metadata
    """
    try:
        meta = getattr(model, TABLE_META_ATTR)
        return meta if isinstance(meta, TableMeta) else None
    except AttributeError:
        return None


def get_column_meta(col: Column) -> ColumnMeta or None:
    """
    Retrieve the column metadata from a column.  If there is no column metadata, the function
    return `None`.

    :param col: the column
    :return: the column metadata
    """
    try:
        meta = getattr(col, COLUMN_META_ATTR)
        return meta if isinstance(meta, ColumnMeta) else None
    except AttributeError:
        return None


def has_column_meta(obj: object) -> bool:
    """
    Test an object to see if it has an attached :py:class:`ColumnMeta` object.

    :param obj: the object
    :return: `True` if the object is a :py:class:`Column` or a
        :py:class:`sqlalchemy.orm.InstrumentedAttribute` with attached column metadata.
    """
    return (isinstance(obj, (Column, InstrumentedAttribute)) and
            hasattr(obj, COLUMN_META_ATTR))
