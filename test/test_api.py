# -*- coding: utf-8 -*-
""" Tests for Content API """

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
import unittest

from resources.lib.sbs.api import SbsApi
from resources.lib.sbs.auth import SbsAuth

_LOGGER = logging.getLogger('test-api')


class TestApi(unittest.TestCase):
    """ Tests for Content API """

    def __init__(self, *args, **kwargs):
        super(TestApi, self).__init__(*args, **kwargs)
        self._auth = SbsAuth(os.getenv('VVZ_USERNAME', ''), os.getenv('VVZ_PASSWORD', ''))

    def test_notifications(self):
        api = SbsApi(self._auth.get_token())
        notifications = api.get_notifications()

        _LOGGER.debug(notifications)


if __name__ == '__main__':
    unittest.main()
