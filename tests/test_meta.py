#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/5/18

from parameterized import parameterized
import unittest
from modlit.meta import (
    ColumnMeta, Requirement, Source, TableMeta, Target, Usage,
    _MetaDescription, _Synonyms
)


class TestMetaDescriptionSuite(unittest.TestCase):
    """
    This suite contains generalized tests of the :py:class:`_MetaDescription`
    abstract class.
    """
    @parameterized.expand([
        (
                Target(),
                Source()
        ),
        (
                Target(guaranteed=True),
                Target(guaranteed=False)
        ),
        (
                Source(synonyms=['a', 'b', 'c']),
                Source(synonyms=['d', 'e', 'f'])
        ),
    ])
    def test_nonEqualObjects_testEqual_notEqual(
            self,
            meta_1,
            meta_2
    ):
        """
        Arrange: two non-equivalent meta-description objects
        Act: test equality
        Assert: not equal

        :param meta_1: a meta-description object
        :type meta_1: :py:class:`_MetaDescription`
        :param meta_2: a meta-description object
        :type meta_2: :py:class:`_MetaDescription`
        """
        self.assertNotEqual(meta_1, meta_2)


class TestSynonymsSuite(unittest.TestCase):
    """
    This suite contains generalized tests of the :py:class:`_Synonyms`
    abstract class.
    """
    @parameterized.expand([
        (
                _Synonyms(['a', 'b', 'c']),
                _Synonyms(['d', 'e', 'f'])
        ),
        (
                _Synonyms(['a', 'b', 'c']),
                ['a', 'b', 'c']
        ),
    ])
    def test_differentSynonyms_testEqual_notEqual(
            self,
            synonyms_1,
            synonyms_2
    ):
        """
        Arrange: two non-equivalent synonym objects
        Act: test equality
        Assert: not equal

        :param synonyms_1: a synonyms object
        :type synonyms_1: :py:class:`_Synonyms`
        :param synonyms_2: a synonyms object
        :type synonyms_2: :py:class:`_Synonyms`
        """
        self.assertNotEqual(synonyms_1, synonyms_2)


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
                ['kappa', 'eta', 'theta']
        ),
        (
                Source(requirement=Requirement.REQUIRED,
                       synonyms=['alpha[0-9]']),
                ['Kappa', 'Eta', 'Theta']
        )
    ])
    def test_init_isSynonym_assertFalse(self,
                                       source,
                                       synonyms):
        """
        Arrange: We need a source and non-synonyms for the source.
        Act: Test candidate synonyms using is_synonym().
        Assert: is_synonym() returns `False` for non-synonyms
        :param source: the source
        :type source: :py:class:`Source`
        :param synonyms: non-synonyms
        :type synonyms: List[str]
        """
        for synonym in synonyms:
            self.assertFalse(source.is_synonym(synonym),
                             f'{synonym} is not a synonym.')

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
    """
    This suite tests the :py:class:`TableMeta` class.
    """
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
        """
        Arrange/Act: Initialize a new column-meta from the arguments supplied.
        Assert: The constructed column-meta is equivalent to the target supplied
            as the `expected` argument

        :param label: the value of the column-meta's `label` attribute
        :type label: `str`
        :param description: the value of the column-meta's `description`
            attribute
        :type description: `str`
        :param nena: the value of the column-meta's `nena` attribute
        :type nena: str
        :param source: the value of the column-meta's `source` attribute
        :type source: :py:class:`Source`
        :param target: the value of the column-meta's `target` attribute
        :type target: :py:class:`Target`
        :param expected: a column-meta that is equal to the one constructed
            from the other arguments
        :type expected: :py:class:`ColumnMeta`
        """
        # Arrange/Act.
        meta = ColumnMeta(label=label, description=description, nena=nena,
                          source=source, target=target)
        # Assert.
        self.assertEqual(expected, meta)
        # To complete coverage...
        self.assertEqual(label, expected.label)
        _ = expected.description
        self.assertEqual(nena, expected.nena)
        self.assertEqual(source, expected.source)
        self.assertEqual(target, expected.target)
        self.assertEqual(source.requirement, expected.get_enum(Requirement))
        self.assertEqual(target.usage, expected.get_enum(Usage))


class TestTableMetaSuite(unittest.TestCase):
    """
    This suite tests the :py:class:`TableMeta` class.
    """

    @parameterized.expand([
        (
                'Label', ['alpha', 'beta', 'gamma'],
                TableMeta(label='Label', synonyms=['alpha', 'beta', 'gamma'])
        ),
    ])
    def test_init_expectedValues(self,
                                 label,
                                 synonyms,
                                 expected):
        """
        Arrange/Act: Initialize a new table-meta from the arguments supplied.
        Assert: The constructed table-meta is equivalent to the target supplied
            as the `expected` argument

        :param label: the value of the column-meta's `label` attribute
        :type label: `str`
        :param synonyms: synonyms
        :type synonyms: Iterable[str]
        :param expected: a table-meta object equal to the one constructed from
            the supplied arguments
        :type expected: :py:class:`TableMeta`
        """
        # Arrange/Act.
        meta = TableMeta(label=label, synonyms=synonyms)
        # Assert.
        self.assertEqual(expected, meta)
        # To complete coverage...
        self.assertEqual(label, expected.label)


if __name__ == '__main__':
    unittest.main()

