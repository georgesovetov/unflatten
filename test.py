import unittest

from unflatten import _path_tuples_with_values_to_dict_tree, dot_colon_join, dot_colon_split
from unflatten import _recognize_lists
from unflatten import _tree_to_path_tuples_with_values
from unflatten import brackets_join
from unflatten import flatten
from unflatten import unflatten


class BracketsReduceTestCase(unittest.TestCase):
    def test_one_element(self):
        self.assertEqual(brackets_join(['aa']), 'aa')

    def test_simple(self):
        self.assertEqual(brackets_join(['aa', 1, 'bb', 2]), 'aa[1][bb][2]')


class TreeToPathTuplesWithValuesTestCase(unittest.TestCase):
    def test_simple(self):
        self.assertSequenceEqual(
            list(_tree_to_path_tuples_with_values(
                {'a': ['b',
                       {'e': 1}]})),
            [(('a', 0), 'b'),
             (('a', 1, 'e'), 1)])


class PathTuplesWithValuesToDictTreeTestCase(unittest.TestCase):
    def test_simple(self):
        self.assertDictEqual(
            _path_tuples_with_values_to_dict_tree(
                [(('a', 0), 'b'),
                 (('a', 1, 'e'), 1)]),
            {'a': {0: 'b',
                   1: {'e': 1}}})


class RecognizeListsTestCase(unittest.TestCase):
    def test_simple(self):
        self.assertListEqual(
            _recognize_lists(
                {0: 'a',
                 1: {'b': -1,
                     'c': {0: 'd',
                           1: -2}}}),
            ['a',
             {'b': -1,
              'c': ['d',
                    -2]}])

    def test_again(self):
        self.assertDictEqual(
            unflatten(
                {'a': 1,
                 'b': {0: 'c',
                       1: {0: 'd',
                           1: {'e': {'f': -1,
                                     'g': 'h'}}}}}),
            {'a': 1,
             'b': ['c',
                   ['d',
                    {'e': {'f': -1,
                           'g': 'h'}}]]})


class FlattenTestCase(unittest.TestCase):
    def test_simple(self):
        self.assertDictEqual(
            flatten(
                {'a': 1,
                 'b': ['c',
                       ['d',
                        {'e': {'f': -1,
                               'g': 'h'}}]]}),
            {'a': 1,
             'b[0]': 'c',
             'b[1][0]': 'd',
             'b[1][1][e][f]': -1,
             'b[1][1][e][g]': 'h'})

    def test_dot_colon(self):
        self.assertDictEqual(
            flatten(
                {'a': 1,
                 'b': ['c',
                       ['d',
                        {'e': {'f': -1,
                               'g': 'h'}}]]},
                join=dot_colon_join),
            {'a': 1,
             'b:0': 'c',
             'b:1:0': 'd',
             'b:1:1.e.f': -1,
             'b:1:1.e.g': 'h'})


class UnflattenTestCase(unittest.TestCase):
    def test_simple(self):
        self.assertDictEqual(
            unflatten(
                {'a': 1,
                 'b[0]': 'c',
                 'b[1][0]': 'd',
                 'b[1][1][e][f]': -1,
                 'b[1][1][e][g]': 'h'}),
            {'a': 1,
             'b': ['c',
                   ['d',
                    {'e': {'f': -1,
                           'g': 'h'}}]]})

    def test_dot_colon(self):
        self.assertDictEqual(
            unflatten(
                {'a': 1,
                 'b:0': 'c',
                 'b:1:0': 'd',
                 'b:1:1.e.f': -1,
                 'b:1:1.e.g': 'h'},
                split=dot_colon_split),
            {'a': 1,
             'b': ['c',
                   ['d',
                    {'e': {'f': -1,
                           'g': 'h'}}]]})


class DotColonJoinTestCase(unittest.TestCase):
    def test_simple(self):
        self.assertSequenceEqual(dot_colon_join(('a',)), 'a')
        self.assertSequenceEqual(dot_colon_join(('b', 0)), 'b:0')
        self.assertSequenceEqual(dot_colon_join(('b', 1)), 'b:1')
        self.assertSequenceEqual(dot_colon_join(('b', 2, 'e')), 'b:2.e')
        self.assertSequenceEqual(dot_colon_join(('b', 2, 'f')), 'b:2.f')


class DotColonSplitTestCase(unittest.TestCase):
    def test_simple(self):
        self.assertTupleEqual(dot_colon_split('a'), ('a',))
        self.assertTupleEqual(dot_colon_split('b:0'), ('b', 0))
        self.assertTupleEqual(dot_colon_split('b:1'), ('b', 1))
        self.assertTupleEqual(dot_colon_split('b:2.e'), ('b', 2, 'e'))
        self.assertTupleEqual(dot_colon_split('b:2.f'), ('b', 2, 'f'))
