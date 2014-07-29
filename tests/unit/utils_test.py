import unittest

from utils import mustach_dict

class TestMustachDict(unittest.TestCase):
    def test_empty(self):
        "mustach an empty dict"
        actual = mustach_dict({})
        self.assertEqual(actual, {})

    def test_no_change(self):
        value = {'a': 1, 'b': 2, 'c': 3}
        actual = mustach_dict(value)
        self.assertEqual(actual, value)

    def test_no_same_key(self):
        value = {'a.b': 1, 'b.c': 2, 'c.d.e':3, 'f':4}
        actual = mustach_dict(value)
        expected = {'a': {'b': 1}, 'b': {'c': 2}, 'c': {'d': {'e': 3}}, 'f': 4}
        self.assertEqual(actual, expected)

    def test_shared_key(self):
        value = {'a.b.c': 1, 'a.b.d': 2, 'a.d.e.f': 3, 'a.d.e.g': 4, 'h':5}
        actual = mustach_dict(value)
        expected = {'a': {'b': {'c': 1, 'd': 2}, 'd': {'e': {'f': 3, 'g': 4}}}, 'h': 5}
        self.assertEqual(actual, expected)

    def test_fail_case(self):
        value = {'a.b':1, 'a.b.c':2, 'a.b.c.d': 3}
        with self.assertRaises(Exception):
            print mustach_dict(value)
