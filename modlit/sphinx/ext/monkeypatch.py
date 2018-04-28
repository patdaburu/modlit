#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/19/18
"""
.. currentmodule:: monkeypatch
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains monkeypatches for Sphinx.
"""
# pylint: skip-file

from docutils import nodes
from sphinx.util.docfields import TypedField
from sphinx import addnodes


def monkeypatch():
    """
    Apply the monkeypatches.
    """
    def patched_make_field(self, types, domain, items, env=None):
        """
        This is a monkeypatch that prevents ivar cross references.

        :param self:
        :param types:
        :param domain:
        :param items:
        :param env:
        :return:

        .. seealso::

            https://stackoverflow.com/questions/31784830/sphinx-ivar-tag-goes-looking-for-cross-references
        """
        # type: (List, unicode, Tuple) -> nodes.field
        def handle_item(fieldarg, content):
            par = nodes.paragraph()
            par += addnodes.literal_strong('', fieldarg)  # Patch: this line added
            if fieldarg in types:
                par += nodes.Text(' (')
                # NOTE: using .pop() here to prevent a single type node to be
                # inserted twice into the doctree, which leads to
                # inconsistencies later when references are resolved
                fieldtype = types.pop(fieldarg)
                if len(fieldtype) == 1 and isinstance(fieldtype[0], nodes.Text):
                    typename = u''.join(n.astext() for n in fieldtype)
                    par.extend(self.make_xrefs(self.typerolename, domain, typename,
                                               addnodes.literal_emphasis))
                else:
                    par += fieldtype
                par += nodes.Text(')')
            par += nodes.Text(' -- ')
            par += content
            return par

        fieldname = nodes.field_name('', self.label)
        if len(items) == 1 and self.can_collapse:
            fieldarg, content = items[0]
            bodynode = handle_item(fieldarg, content)
        else:
            bodynode = self.list_type()
            for fieldarg, content in items:
                bodynode += nodes.list_item('', handle_item(fieldarg, content))
        fieldbody = nodes.field_body('', bodynode)
        return nodes.field('', fieldname, fieldbody)

    TypedField.make_field = patched_make_field
