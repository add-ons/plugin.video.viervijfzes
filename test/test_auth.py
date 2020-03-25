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

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_login(self):
        # Clear any cache we have
        AuthApi.clear_tokens()

        # We should get a token by logging in
        auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'))
        token = auth.get_token()
        self.assertTrue(token)

        # Test it a second time, it should go from memory now
        auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'))
        token = auth.get_token()
        self.assertTrue(token)


if __name__ == '__main__':
    unittest.main()
