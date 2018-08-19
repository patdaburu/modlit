#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: modlit.flask
.. moduleauthor:: Pat Blair <pblair@geo-comm.com>

Look in here for `Flask-RESTPlus <http://flask-restplus.readthedocs.io/en/stable/>`_ extensions.

:var SQA_RESTPLUS_TYPES:  a mapping of SqlAlchemy types to marshmallow field
    type constructors.
"""

import inspect
import logging
from typing import Type
from flask_restplus import Model, Namespace, fields
from sqlalchemy.orm.attributes import InstrumentedAttribute
import sqlalchemy.sql.sqltypes
from .meta import has_column_meta

SQA_RESTPLUS_TYPES = {
    #GUID: fields.UUID,  # TODO: Figure out how to handle GUIDs.
    sqlalchemy.types.BigInteger: fields.Integer,
    sqlalchemy.types.Boolean: fields.Boolean,
    sqlalchemy.types.Date: fields.DateTime,
    sqlalchemy.types.Float: fields.Float,
    sqlalchemy.types.Integer: fields.Integer,
    sqlalchemy.types.Text: fields.String,
    sqlalchemy.types.Time: fields.DateTime,
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
    sqlalchemy.sql.sqltypes.TIME: fields.DateTime,
    sqlalchemy.sql.sqltypes.TIMESTAMP: fields.DateTime,
    sqlalchemy.sql.sqltypes.VARCHAR: fields.String
}

_logger = logging.getLogger(__name__)  #: the module's logger


def api_model(cls: Type, ns: Namespace, name: str = None) -> Model:
    """
    Generate a Flask-RESTPlus model for a class.

    :param cls: the class
    :param ns: the Flask-RESTPlus API namespace
    :param name: the preferred name of the model
    :return: the Flask-RESTPlus model
    """
    # If a name is provided, use it.  Otherwise we'll go with the class' name.
    _name = name if name else cls.__name__

    # If we find that a model with this name has already been created...
    if _name in ns.models:
        # ...just return it.
        return ns.models[_name]

    # Create a dictionary to hold attribute values we'll use to construct our
    # dynamic Schema class.
    fields_ = {}

    # We think this is a SQLAlchemy class.  Moreover, we expect it's a modlit
    # model.  So, we're interested in attributes that appear to be SQLAlchemy
    # `InstrumentedAttribute` instances that also have column metadata attached.
    for attr_name, sqa_attr in [
            member for member in inspect.getmembers(cls)
            if isinstance(member[1], InstrumentedAttribute)
            and has_column_meta(member[1])
    ]:
#        col_meta = get_column_meta(sqa_attr)  # TODO: Figure out the "required" business.
        sqa_type = sqa_attr.property.columns[0].type
        try:
            mm_type = SQA_RESTPLUS_TYPES[type(sqa_type)]
            fields_[attr_name] = mm_type()
        except KeyError:
            _logger.warning(
                f'The {cls.__name__}.{attr_name} is of type {type(sqa_type)}'
                f'but there is no equivalent Flask-RESTPlus type so the '
                f'attribute is not included in the API model.'
            )
    # We should now have enough information to create the model.
    return ns.model(_name, fields_)


class ApiModelMixin(object):
    """
    Mix this into your class to create a Flask-RESTPlus API.
    """
    @classmethod
    def api_model(cls, ns: Namespace, name: str = None) -> Model:
        """
        Generate a Flask-RESTPlus model for a class.

        :param ns: the Flask-RESTPlus API namespace
        :param name: the preferred name of the model
        :return: the Flask-RESTPlus model
        """
        return api_model(cls=cls, ns=ns, name=name)
