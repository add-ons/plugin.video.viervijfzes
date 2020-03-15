# -*- coding: utf-8 -*-
""" Tests for Auth """

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import unittest

from resources.lib.sbs.auth import SbsAuth


class TestAuth(unittest.TestCase):
    """ Tests for VTM GO API """

    def __init__(self, *args, **kwargs):
        super(TestAuth, self).__init__(*args, **kwargs)

    def test_login_ok(self):
        # TODO: use a credentials.json or something
        auth = SbsAuth(os.getenv('VVZ_USERNAME', ''), os.getenv('VVZ_PASSWORD', ''))
        token = auth.get_token()
        self.assertTrue(token)

    def test_login_nok(self):
        auth = SbsAuth('unknown@example.com', 'password')
        with self.assertRaises(Exception):
            auth.get_token()


if __name__ == '__main__':
    unittest.main()
