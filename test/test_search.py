# -*- coding: utf-8 -*-
""" Tests for EPG API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

from resources.lib.viervijfzes.content import Program
from resources.lib.viervijfzes.search import SearchApi

_LOGGER = logging.getLogger('test-search')


class TestSearch(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestSearch, self).__init__(*args, **kwargs)
        self._search = SearchApi()

    def test_search(self):
        programs = self._search.search('de mol')
        self.assertIsInstance(programs, list)
        self.assertIsInstance(programs[0], Program)

    def test_search_empty(self):
        programs = self._search.search('')
        self.assertIsInstance(programs, list)

    def test_search_space(self):
        programs = self._search.search(' ')
        self.assertIsInstance(programs, list)


if __name__ == '__main__':
    unittest.main()
