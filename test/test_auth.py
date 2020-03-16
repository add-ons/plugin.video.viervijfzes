# -*- coding: utf-8 -*-
""" Tests for AUTH API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
import unittest

from resources.lib.sbs.auth import SbsAuth

_LOGGER = logging.getLogger('test-auth')


class TestAuth(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAuth, self).__init__(*args, **kwargs)

    def test_login(self):
        # TODO: use a credentials.json or something
        auth = SbsAuth(os.getenv('VVZ_USERNAME', ''), os.getenv('VVZ_PASSWORD', ''), cache='/tmp/viervijfzes-tokens.json')

        # We should get a token by logging in or refreshing
        token = auth.get_token()
        self.assertTrue(token)
        self.assertIsInstance(token, str)

        # Test it a second time, it should go from memory now
        token = auth.get_token()
        self.assertTrue(token)
        self.assertIsInstance(token, str)


if __name__ == '__main__':
    unittest.main()
