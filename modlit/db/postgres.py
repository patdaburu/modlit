#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/8/18
"""
.. currentmodule:: modlit.db.postgres
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains utilities for working directly with PostgreSQL.
"""
import json
from pathlib import Path
from urllib.parse import urlparse, ParseResult
from typing import Iterable, List
from addict import Dict
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sqlalchemy.types
#from ..meta import ColumnMeta, TableMeta, get_column_meta, get_table_meta
#from ..transform import ModelMap
from .db import ColumnInfo, TableInfo


DEFAULT_ADMIN_DB = 'postgres'  #: the default administrative database name
DEFAULT_PG_PORT = 5432  #: the default PostgreSQL listener port

# Load the Postgres phrasebook.
# pylint: disable=invalid-name
# pylint: disable=no-member
_sql_phrasebook = Dict(
    json.loads(
        (
            Path(__file__).resolve().parent / 'postgres.json'
        ).read_text()
    )['sql']
)

_pg2orm_data_types = {
    'integer': sqlalchemy.types.Integer,
    'double precision': sqlalchemy.types.Float,
    'character varying': sqlalchemy.types.String
}  #: a mapping of Postgres data type names to SQLAlchemy data types


def connect(url: str, dbname: str = None, autocommit: bool = False):
    """
    Create a connection to a Postgres database.

    :param url: the Postgres instance URL
    :param dbname: the target database name (if it differs from the one
        specified in the URL)
    :param autocommit: Set the `autocommit` flag on the connection?
    :return: a psycopg2 connection
    """
    # Parse the URL.  (We'll need the pieces to construct an ogr2ogr connection
    # string.)
    dbp: ParseResult = urlparse(url)
    # Create a dictionary to hold the arguments for the connection.  (We'll
    # unpack it later.)
    cnx_opt = {
        k: v for k, v in
        {
            'host': dbp.hostname,
            'port': int(dbp.port) if dbp.port is not None else DEFAULT_PG_PORT,
            'database': dbname if dbname is not None else dbp.path[1:],
            'user': dbp.username,
            'password': dbp.password
        }.items() if v is not None
    }
    cnx = psycopg2.connect(**cnx_opt)
    # If the caller requested that the 'autocommit' flag be set...
    if autocommit:
        # ...do that now.
        cnx.autocommit = True
    return cnx


def db_exists(url: str,
              dbname: str = None,
              admindb: str = DEFAULT_ADMIN_DB) -> bool:
    """
    Does a given database on a Postgres instance exist?

    :param url: the Postgres instance URL
    :param dbname: the name of the database to test
    :param admindb: the name of an existing (presumably the main) database
    :return: `True` if the database exists, otherwise `False`
    """
    # Let's see what we got for the database name.
    _dbname = dbname
    # If the caller didn't specify a database name...
    if not _dbname:
        # ...let's figure it out from the URL.
        db: ParseResult = urlparse(url)
        _dbname = db.path[1:]
    # Now, let's do this!
    with connect(url=url, dbname=admindb) as cnx:
        with cnx.cursor() as crs:
            # Execute the SQL query that counts the databases with a specified
            # name.
            crs.execute(
                _sql_phrasebook.select_db_count.format(_dbname)
            )
            # If the count isn't zero (0) the database exists.
            return crs.fetchone()[0] != 0


def create_db(
        url: str,
        dbname: str,
        admindb: str = DEFAULT_ADMIN_DB):
    """
    Create a database on a Postgres instance.

    :param url: the Postgres instance URL
    :param dbname: the name of the database
    :param admindb: the name of an existing (presumably the main) database
    """
    with connect(url=url, dbname=admindb) as cnx:
        cnx.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with cnx.cursor() as crs:
            crs.execute(_sql_phrasebook.create_db.format(dbname))


def touch_db(
        url: str,
        dbname: str = None,
        admindb: str = DEFAULT_ADMIN_DB):
    """
    Create a database if it does not already exist.

    :param url: the Postgres instance URL
    :param dbname: the name of the database
    :param admindb: the name of an existing (presumably the main) database
    """
    # If the database already exists, we don't need to do anything further.
    if db_exists(url=url, dbname=dbname, admindb=admindb):
        return
    # Let's see what we got for the database name.
    _dbname = dbname
    # If the caller didn't specify a database name...
    if not _dbname:
        # ...let's figure it out from the URL.
        db: ParseResult = urlparse(url)
        _dbname = db.path[1:]
    # Now we can create it.
    create_db(url=url, dbname=_dbname, admindb=admindb)


def get_tables(url: str, schema: str = None) -> Iterable[TableInfo]:
    """
    Get information about tables in the database.

    :param url: the URL of the database
    :param schema: the target schema
    :return: an iteration of :py:class:`TableInfo` objects
    """
    # Based on whether or not the caller supplied a schema, let's select a
    # SQL statement from the phrasebook and prepare it.
    tbl_sql = (
        _sql_phrasebook.select_tables_in_schema.format(schema)
        if schema
        else _sql_phrasebook.select_tables
    )
    # Connect to the database.
    with connect(url=url) as cnx, \
            cnx.cursor(cursor_factory=DictCursor) as tbl_crs:
        tbl_crs.execute(tbl_sql)
        # Now let's go through the tables.
        for rec in tbl_crs:
            # Grab the information about the table and schema.
            table_name = rec['table_name']
            schema = rec['table_schema']
            # Next we're going to get the columns.
            cols: List(ColumnInfo) = []
            with cnx.cursor(cursor_factory=DictCursor) as col_crs:
                col_crs.execute(
                    _sql_phrasebook.select_columns.format(schema, table_name)
                )
                for col_rec in col_crs:
                    # Retrieve the column name...
                    column_name = col_rec['column_name']
                    # ...and data type as reported by the database.
                    data_type = col_rec['data_type']
                    print(data_type)
                    # Retrieve the ORM type that matches the reported data
                    # type.  (If we don't have a matching, we'll use a default.)
                    orm_type = (
                        _pg2orm_data_types[data_type]
                        if data_type in _pg2orm_data_types
                        else sqlalchemy.types.MatchType
                    )
                    cols.append(
                        ColumnInfo(column_name=column_name,
                                   orm_type=orm_type)
                    )
            # Now that we have all the columns, we can yield the table info
            # to the caller.
            yield TableInfo(
                table_name=table_name,
                schema=schema,
                columns=cols
            )


class AutoModelMapper(object):
    """
    Use an automatic model mapper to find candidate mappings for tables in
    your PostgreSQL database.
    """
    def __init__(self, url: str, schema: str = None):
        """

        :param url: the database URL
        :param schema: the schema that contains candidate data
        """
        # Hang on to the database URL.
        self._url = url
        self._schema = schema
        # Go ahead and connect to the database.
        self._cnx = connect(url=url)

    # def get_candidate_tables(self, model):
    #     """
    #
    #     :param model:
    #     :return:
    #     """
    #     table_meta = get_table_meta(model)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cnx.close()
