#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/6/18
"""
.. currentmodule:: api
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module defines classes you can use to develop APIs for your model.
"""
from flask import Flask
from sqlalchemy.engine.base import Engine
from .errors import ModlitError


class EngineMixin(object):
    """
    This mixin provides an :py:class:`Engine` property along with a function
    for installing one.
    """

    _engine_attr = '__engine__'  #: the name of the engine attribute

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
        else: # We have a problem.
            raise ModlitError('The engine has already been installed.')


class ModlitFlask(Flask, EngineMixin):
    """
    This is a `Flask application object <http://flask.pocoo.org/docs/0.12/api/#application-object>`
    with some additional features to help you build an API around your model.
    """
    pass