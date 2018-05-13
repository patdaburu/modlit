#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/8/18
"""
.. currentmodule:: modlit.db
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Say something descriptive about the 'db' module.
"""
import logging
from pathlib import Path
from sqlalchemy.engine.base import Engine
import sqlparse


def exec_sql(engine: Engine, path: Path):
    """
    Call this function to execute the SQL statements within a file against
    your database.

    :param engine: the engine connected to the database
    :param path: the path to the containing your SQL statements
    """
    with engine.connect() as connection:
        logger: logging.Logger = logging.getLogger(__name__)
        for sql_stmt in sqlparse.split(path.read_text().strip()):
            # Parse the statement so that we may detect comments.
            sqlp = sqlparse.parse(sql_stmt)
            # If the parsed statement has only one token and it's statement
            # type is 'unknown'...
            if len(sqlp) == 1 and sqlp[0].get_type() == 'UNKNOWN':
                # ...move along.  This is likely a comment and will cause an
                # exception if we try to execute it by itself.
                continue
            # We're all set.  Execute the statement.
            logger.debug(sql_stmt)
            connection.execute(sql_stmt)
