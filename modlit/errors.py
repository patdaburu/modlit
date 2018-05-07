#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/6/18
"""
.. currentmodule:: errors
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Something went wrong?  OK.  Here's what we'll do...
"""


class ModlitError(Exception):
    """
    A general error pertaining to things that happen in the `modlit` package.
    """
    def __init__(self, message: str):
        """

        :param message: the error message
        """
        super().__init__()
        self._message = message

    @property
    def message(self) -> str:
        """
        Get the error message.

        :return: the error message
        """
        return self._message
