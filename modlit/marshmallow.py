#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created on 7/28/18 by Pat Blair
"""
.. currentmodule:: modlit.marshmallow
.. moduleauthor:: Pat Blair <pblair@geo-comm.com>

`Marshmallow <https://marshmallow.readthedocs.io/en/3.0/>`_ is all about simplified object
serialization.
"""
import inspect
from typing import cast, Type
from marshmallow import Schema, fields, post_load #, pprint, post_load, ValidationError, validates
from sqlalchemy.orm.attributes import InstrumentedAttribute
import sqlalchemy.sql.sqltypes
from .types import GUID
from .meta import has_column_meta, get_column_meta


MM_SCHEMA_ATTR = '__marshmallow_schema__'


# See http://docs.sqlalchemy.org/en/latest/core/type_basics.html
SQA_MM_TYPES = {
    GUID: fields.UUID,
    sqlalchemy.types.BigInteger: fields.Integer,
    sqlalchemy.types.Boolean: fields.Boolean,
    sqlalchemy.types.Date: fields.DateTime,
    sqlalchemy.types.Float: fields.Float,
    sqlalchemy.types.Integer: fields.Integer,
    sqlalchemy.types.Text: fields.String,
    sqlalchemy.types.Time: fields.Time,
    sqlalchemy.sql.sqltypes.String: fields.String,
    sqlalchemy.sql.sqltypes.BIGINT: fields.Integer,
    sqlalchemy.sql.sqltypes.BOOLEAN: fields.Boolean,
    sqlalchemy.sql.sqltypes.CHAR: fields.String,
    sqlalchemy.sql.sqltypes.DATE: fields.Date,
    sqlalchemy.sql.sqltypes.DATETIME: fields.DateTime,
    sqlalchemy.sql.sqltypes.DECIMAL: fields.Float,
    sqlalchemy.sql.sqltypes.FLOAT: fields.Float,
    sqlalchemy.sql.sqltypes.INT: fields.Integer,
    sqlalchemy.sql.sqltypes.INTEGER: fields.Integer,
    sqlalchemy.sql.sqltypes.NCHAR: fields.String,
    sqlalchemy.sql.sqltypes.NVARCHAR: fields.String,
    sqlalchemy.sql.sqltypes.NUMERIC: fields.Float,
    sqlalchemy.sql.sqltypes.REAL: fields.Float,
    sqlalchemy.sql.sqltypes.SMALLINT: fields.Integer,
    sqlalchemy.sql.sqltypes.TEXT: fields.String,
    sqlalchemy.sql.sqltypes.TIME: fields.Time,
    sqlalchemy.sql.sqltypes.TIMESTAMP: fields.DateTime,
    sqlalchemy.sql.sqltypes.VARCHAR: fields.String
}  #: a mapping of SqlAlchemy types to marshmallow field type constructors.


def mm_schema(cls: Type, name: str = None, cache: bool = True) -> Schema:
    """
    Generate a
    `Marshmallow schema <https://marshmallow.readthedocs.io/en/3.0/api_reference.html#schema>`_
    for a class.

    :param cls: the data class for which you need a schema
    :param name: the preferred name of the generated schema class  (If no argument is provided we
        create a name based on the class name.)
    :param cache: `True` to cache the generated schema for subsequent calls (or used the
        cached schema), `False` to ignore caching
    :return: the generated Marshmallow schema
    """
    # If we're employing a caching strategy (so we don't have to do this over and over)...
    if cache:
        # ...try to return any previously-generated schema.
        try:
            # ...it should be waiting and we can return it.
            return getattr(cls, MM_SCHEMA_ATTR)
        except AttributeError:
            pass  # That's all right.  It just means we haven't generated it yet.

    # What shall we call the schema class?
    _clsname = name if name else f'{cls.__name__}Schema'

    # Create a dictionary to hold attribute values we'll use to construct our dynamic Schema
    # class.
    attrs_ = {}

    # We think this is a SQLAlchemy class.  Moreover, we expect it's a modlit model.
    # So, we're interested in attributes that appear to be SQLAlchemy `InstrumentedAttribute`
    # instances that also have column metadata attached.
    for attr_name, sqa_attr in [
            member for member in inspect.getmembers(cls)
            if isinstance(member[1], InstrumentedAttribute)
            and has_column_meta(member[1])
    ]:
        col_meta = get_column_meta(sqa_attr)
        sqa_type = sqa_attr.property.columns[0].type
        try:
            mm_type = SQA_MM_TYPES[type(sqa_type)]
            attrs_[col_meta.label] = mm_type(description=col_meta.description)
        except KeyError:
            print(f'***********DID NOT FIND A MM TYPE FOR {sqa_type}')  #: TODO: Logging!!!!

    # Add the post-load function to create an instance of the object.
    def _post_load(_, __, original_data):  # _ = self, __ = data
        obj = cls()
        for key in original_data:
            print(key)
            setattr(obj, key, original_data[key])
        return obj

    attrs_['_post_load'] = post_load(fn=_post_load, pass_original=True)

    # _post_load = post_load(fn=lambda _, data: cls().init(data))
    # attrs_['_post_load'] = _post_load



    # Create the schema class.
    schema_cls = type(_clsname, (Schema,), attrs_)
    # Now create an instance.
    schema_obj = schema_cls()
    # If we're caching, stash it in the class for next time.
    if cache:
        setattr(cls, MM_SCHEMA_ATTR, schema_obj)
    # That should be that.
    return cast(Schema, schema_obj)


class MarshmallowSchemaMixin(object):
    """
    Mix this into your data class if you need a
    `Marshmallow schema <https://marshmallow.readthedocs.io/en/3.0/api_reference.html#schema>`_
    representation of your object.

    .. seealso::

        :py:func:`schema`
    """
    @classmethod
    def mm_schema(cls) -> Schema:
        """
        Get a
        `Marshmallow schema <https://marshmallow.readthedocs.io/en/3.0/api_reference.html#schema>`_
        to use with this model class.

        :return: the marshmallow schema
        """
        return mm_schema(cls, cache=True)




