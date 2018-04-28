#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/14/18
"""
.. currentmodule:: modlit.geometry
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains stuff pertaining to geometry columns.
"""

from enum import IntFlag


class GeometryTypes(IntFlag):
    """
    Supported geometry types.
    """
    NONE = 0  #: no geometry type
    POINT = 1  #: point geometries
    LINESTRING = 2  #: polyline geometries
    POLYGON = 4  #: polygon geometries
    GEOMETRY = 7  #: generic geometries
    CURVE = 8  #: curves
    MULTIPOINT = 17  #: multipoint collections
    MULTILINESTRING = 18  #: multilinestring collections
    MULTIPOLYGON = 20  #: multipolygon collections
    GEOMETRYCOLLECTION = 23  #: geometry collections
