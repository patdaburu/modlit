#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/6/18
"""
.. currentmodule:: api
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module defines classes you can use to develop APIs for your model.
"""
from typing import List
from flask import Flask
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from .errors import ModlitError
from .modules import walk_load


class EngineMixin(object):
    """
    This mixin provides an :py:class:`Engine` property along with a function
    for installing one.
    """

    _engine_attr = '__engine__'
    _sessionmaker_attr = '__sessionmaker__'

    @property
    def engine(self) -> Engine:
        """
        Get the SQLAlchemy engine for the application.

        :return: the SQLAlchemy engine
        """
        try:
            return getattr(self, self._engine_attr)
        except AttributeError:
            raise ModlitError(
                'No engine has been installed. '
                'Use the install_engine() function.'
            )

    def install_engine(self, engine: Engine):
        """
        Install the SQLAlchemy engine for the app.

        :param engine: the engine
        :raises ModlitError: if an engine has already been installed
        """
        # If no engine was installed previously...
        if not hasattr(self, self._engine_attr):
            # ...this one will do.
            setattr(self, self._engine_attr, engine)
            # We can also now create a session maker and bind it to the
            # engine.
            setattr(self, self._sessionmaker_attr, sessionmaker(bind=engine))
        else:  # We have a problem.
            raise ModlitError('The engine has already been installed.')

    def session(self):
        """
        Get a new session.

        :return: the new session
        :raises ModlitError: if the engine has not been installed
        """
        try:
            _sessionmaker = getattr(self, self._sessionmaker_attr)
            return _sessionmaker()
        except AttributeError:
            raise ModlitError(
                'The sessionmaker has not been initialized. '
                'This likely means no engine is installed. '
                'Use the install_engine() function.'
            )


class ModlitFlask(Flask, EngineMixin):
    """
    This is a `Flask application object <http://flask.pocoo.org/docs/0.12/api/#application-object>`
    with some additional features to help you build an API around your model.
    """
    pass


def load_routes(package, skip_modules: List[str] = None):
    """
    Load the data model.

    :param package: the package that contains the model classes
    :param skip_modules: a list of names of the modules that should be skipped
        when importing the package
    """
    walk_load(package, skip_modules=skip_modules)
