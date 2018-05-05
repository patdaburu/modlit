#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/5/18

from parameterized import parameterized
import unittest
from modlit.meta import ColumnMeta, Requirement, Source, Target, Usage


class TestTargetSuite(unittest.TestCase):

    @parameterized.expand([
        # (
        #         True, True, Usage.SEARCH,
        #         Target(guaranteed=True,
        #                calculated=True,
        #                usage=Usage.SEARCH)
        # ),
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
        # Arrange/Act.
        target = Target(guaranteed=guaranteed,
                        calculated=calculated,
                        usage=usage)
        # Assert.
        self.assertEqual(expected, target)
        self.assertNotEqual(expected, 1)
        print(f'expected = {expected}')


# class TestColumnMetaSuite(unittest.TestCase):
#
#     @parameterized.expand([
#         (
#                 'Label', 'Description', 'NENA',
#                 Source(Requirement.REQUIRED),
#                 Target(guaranteed=True, calculated=True, usage=Usage.DISPLAY),
#                 ColumnMeta(
#                     label='Label', description='Description', nena='NENA',
#                     source=Source(Requirement.REQUIRED),
#                     target=Target(
#                         guaranteed=True,
#                         calculated=True,
#                         usage=Usage.DISPLAY
#                     )
#                 )
#         ),
#     ])
#     def test_init_expectedValues(self,
#                                  label, description, nena, source, target,
#                                  expected):
#         # Arrange/Act.
#         meta = ColumnMeta(label=label, description=description, nena=nena,
#                           source=source, target=target)
#         # Assert.
#         self.assertEqual(expected, meta)


if __name__ == '__main__':
    unittest.main()

