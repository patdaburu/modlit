#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/11/18
"""
.. currentmodule:: modlit.testing.postgres
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains resources for testing your model against
`PostgreSQL <https://www.postgresql.org/>`_ databases.
"""
import atexit
import testing.postgresql
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine


class TempDatabase(object):
    """
    Create an instance of this class to create a temporary Postgres database
    that will dispose of itself automatically.
    """
    def __init__(self):
        self._postgresql = testing.postgresql.Postgresql()
        self._engine: Engine = create_engine(self._postgresql.url())
        atexit.register(self.shutdown)

    @property
    def engine(self) -> Engine:
        """
        Get a SQLAlchemy engine for the database.

        :return: the SQLAlchemcy engine attached to the database
        """
        return self._engine

    def shutdown(self):
        """
        Shutdown and dispose of the database.
        """
        self._postgresql.stop()
        # We no longer need to worry about cleaning up at shutdown.
        atexit.unregister(self.shutdown)

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.shutdown()
