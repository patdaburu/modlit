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


def create_db(
        url: str,
        dbname: str,
        admindb: str = 'postgres'):
    """
    Create a database on a Postgres instance.

    :param url: the Postgres instance URL
    :param dbname: the name of the database
    :param admindb: the name of an existing (presumably the main) database
    :return:
    """
    with connect(url=url, dbname=admindb) as cnx:
        cnx.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with cnx.cursor() as crs:
            crs.execute(sql_phrasebook.create_db.format(dbname))
