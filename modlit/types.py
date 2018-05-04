"""
.. currentmodule:: modlit.types
.. moduleauthor:: Pat Daburu <pat@dabru.net>

This module contains custom GeoAlchemy/SQLAlchemy types.
"""
# pylint: skip-file

from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid


class GUID(TypeDecorator):
    """
    This is a Platform-independent GUID type that uses PostgreSQL's UUID type
    and otherwise uses CHAR(32), storing as stringified hex values.

    .. seealso::

        http://docs.sqlalchemy.org/en/latest/core/custom_types.html#backend-agnostic-guid-type
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value
