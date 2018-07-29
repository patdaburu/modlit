#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: modlit.flask
.. moduleauthor:: Pat Blair <pblair@geo-comm.com>

Look in here for `Flask-RESTPlus <http://flask-restplus.readthedocs.io/en/stable/>`_ extensions.
"""

import inspect
from typing import Type
from flask_restplus import Namespace, fields
from sqlalchemy.orm.attributes import InstrumentedAttribute
import sqlalchemy.sql.sqltypes
from .meta import has_column_meta, get_column_meta


SQA_RESTPLUS_TYPES = {
    #GUID: fields.UUID,
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
}  #: a mapping of SqlAlchemy types to marshmallow field type constructors.


def api_model(cls: Type, ns: Namespace, name: str = None):

    _name = name if name else cls.__name__

    if _name in ns.models:
        return ns.models[_name]

    # Create a dictionary to hold attribute values we'll use to construct our dynamic Schema
    # class.
    fields = {}

    # We think this is a SQLAlchemy class.  Moreover, we expect it's a modlit model.
    # So, we're interested in attributes that appear to be SQLAlchemy `InstrumentedAttribute`
    # instances that also have column metadata attached.
    for attr_name, sqa_attr in [
            member for member in inspect.getmembers(cls)
            if isinstance(member[1], InstrumentedAttribute)
            and has_column_meta(member[1])
    ]:
        col_meta = get_column_meta(sqa_attr)  # TODO: Figure out the "required" business.
        sqa_type = sqa_attr.property.columns[0].type
        try:
            mm_type = SQA_RESTPLUS_TYPES[type(sqa_type)]
            fields[attr_name] = mm_type()
        except KeyError:
            print(f'***********DID NOT FIND A MM TYPE FOR {sqa_type}')  #: TODO: Logging!!!!

    return ns.model(_name, fields)


class ApiModelMixin(object):

    @classmethod
    def api_model(cls, ns: Namespace, name: str = None):
        """
        Get a
        `Marshmallow schema <https://marshmallow.readthedocs.io/en/3.0/api_reference.html#schema>`_
        to use with this model class.

        :return: the marshmallow schema
        """
        return api_model(cls=cls, ns=ns, name=name)



# Sneetch: api.model = api.model(
#     'Sneetch',
#     {
#         'name': fields.String(
#             required=True,
#             description="the name of the sneetch"
#         ),
#         'stars': fields.Integer(
#             description="the number of belly stars",
#             required=False,
#             default=0
#         )
#     }
# )  #: That day they decided that sneetches are sneetches...