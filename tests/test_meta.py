#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/5/18

from parameterized import parameterized
import unittest
from modlit.meta import (
    ColumnMeta, Requirement, Source, Target, Usage
)


class TestSourceSuite(unittest.TestCase):
    """
    This test suite focuses on the :py:class:`Source` class.
    """
    @parameterized.expand([
        (
                Requirement.NONE, None,
                Source(requirement=Requirement.NONE,
                       synonyms=None)
        ),
        (
                Requirement.REQUIRED, ['alpha', 'beta', 'gamma'],
                Source(requirement=Requirement.REQUIRED,
                       synonyms=['alpha', 'beta', 'gamma'])
        ),
    ])
    def test_init_expectedValues(self,
                                 requirement,
                                 synonyms,
                                 expected):
        """
        Arrange/Act: Initialize a new source from the arguments supplied.
        Assert: The constructed target is equivalent to the source supplied as
            the `expected` argument

        :param requirement: the value of the target's `guaranteed` property
        :type requirement: `Requirement`
        :param synonyms: the value of the target's `calculated` property
        :type synonyms: `Iterable[str]`
        :param expected: a source equivalent to the one described by the other
            arguments
        :type expected: :py:class:`Source`
        """
        # Arrange/Act.
        source = Source(requirement=requirement, synonyms=synonyms)
        # Assert.
        self.assertEqual(expected, source)
        self.assertNotEqual(expected, 1)
        # For coverage completion...
        self.assertEqual(source.requirement, requirement)

    @parameterized.expand([
        (
                Source(requirement=Requirement.REQUIRED,
                       synonyms=['alpha', 'beta', 'gamma']),
                ['alpha', 'beta', 'gamma']
        ),
        (
                Source(requirement=Requirement.REQUIRED,
                       synonyms=['alpha', 'beta', 'gamma']),
                ['Alpha', 'Beta', 'GAMMA']
        )
        ,
        (
                Source(requirement=Requirement.REQUIRED,
                       synonyms=['alpha[0-9]']),
                ['Alpha1', 'Alpha5', 'Alpha9']
        )
    ])
    def test_init_isSynonym_assertTrue(self,
                                       source,
                                       synonyms):
        """
        Arrange: We need a source and candidate synonyms.
        Act: Test candidate synonyms using is_synonym().
        Assert: is_synonym() returns `True` for synonyms
        :param source: the source
        :type source: :py:class:`Source`
        :param synonyms: candidate synonyms
        :type synonyms: List[str]
        """
        for synonym in synonyms:
            self.assertTrue(source.is_synonym(synonym),
                            f'{synonym} is a synonym.')


class TestTargetSuite(unittest.TestCase):
    """
    This test suite focuses on the :py:class:`Target` class.
    """
    @parameterized.expand([
        (
                True, True, Usage.SEARCH,
                Target(guaranteed=True,
                       calculated=True,
                       usage=Usage.SEARCH)
        ),
        (
                True, True, (Usage.SEARCH, Usage.DISPLAY),
                Target(guaranteed=True,
                       calculated=True,
                       usage=Usage.SEARCH | Usage.DISPLAY)
        ),
    ])
    def test_init_expectedValues(self,
                                 guaranteed,
                                 calculated,
                                 usage,
                                 expected):
        """
        Arrange/Act: Initialize a new target from the arguments supplied.
        Assert: The constructed target is equivalent to the target supplied as
            the `expected` argument

        :param guaranteed: the value of the target's `guaranteed` property
        :type guaranteed: `bool`
        :param calculated: the value of the target's `calculated` property
        :type calculated: `bool`
        :param usage: the value of the target's `usage` property
        :type usage: :py:class:`Usage`
        :param expected: a target equivalent to the one described by the other
            arguments
        :type expected: :py:class:`Target`
        """
        # Arrange/Act.
        target = Target(guaranteed=guaranteed,
                        calculated=calculated,
                        usage=usage)
        # Assert.
        self.assertEqual(expected, target)
        self.assertNotEqual(expected, 1)
        # For coverage completion...
        self.assertEqual(guaranteed, target.guaranteed)
        self.assertEqual(calculated, target.calculated)
        # The remaining property accessors pass by not throwing exceptions.
        _ = target.usage


class TestColumnMetaSuite(unittest.TestCase):

    @parameterized.expand([
        (
                'Label', 'Description', 'NENA',
                Source(Requirement.REQUIRED),
                Target(guaranteed=True, calculated=True, usage=Usage.DISPLAY),
                ColumnMeta(
                    label='Label', description='Description', nena='NENA',
                    source=Source(Requirement.REQUIRED),
                    target=Target(
                        guaranteed=True,
                        calculated=True,
                        usage=Usage.DISPLAY
                    )
                )
        ),
    ])
    def test_init_expectedValues(self,
                                 label, description, nena, source, target,
                                 expected):
        # Arrange/Act.
        meta = ColumnMeta(label=label, description=description, nena=nena,
                          source=source, target=target)
        # Assert.
        self.assertEqual(expected, meta)


if __name__ == '__main__':
    unittest.main()

