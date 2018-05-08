#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/8/18
"""
.. currentmodule:: modlit.db
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Say something descriptive about the 'db' module.
"""
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
        for sql_stmt in sqlparse.split(path.read_text().strip()):
            connection.execute(sql_stmt)
