# -*- coding: utf-8 -*-
""" Tests for AUTH API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

from resources.lib import kodiutils
from resources.lib.viervijfzes.auth import AuthApi

_LOGGER = logging.getLogger('test-auth')


class TestAuth(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAuth, self).__init__(*args, **kwargs)
        self._auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())

    def test_login(self):
        # Clear any cache we have
        self._auth.clear_cache()

        # We should get a token by logging in
        token = self._auth.get_token()
        self.assertTrue(token)

        # Test it a second time, it should go from memory now
        token = self._auth.get_token()
        self.assertTrue(token)


if __name__ == '__main__':
    unittest.main()
