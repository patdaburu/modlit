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
from addict import Dict
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


DEFAULT_ADMIN_DB = 'postgres'  #: the default administrative database name

# Load the Postgres phrasebook.
# pylint: disable=invalid-name
# pylint: disable=no-member
sql_phrasebook = Dict(
    json.loads(
        (
            Path(__file__).resolve().parent / 'postgres.json'
        ).read_text()
    )['sql']
)


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
            'port': int(dbp.port),
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
                sql_phrasebook.select_db_count.format(_dbname)
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
            crs.execute(sql_phrasebook.create_db.format(dbname))


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
