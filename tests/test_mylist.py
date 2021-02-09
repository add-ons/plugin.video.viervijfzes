# -*- coding: utf-8 -*-
""" Tests for My List """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

from resources.lib import kodiutils
from resources.lib.viervijfzes.auth import AuthApi

_LOGGER = logging.getLogger(__name__)


class TestMyList(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestMyList, self).__init__(*args, **kwargs)

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_mylist(self):
        auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())
        id_token = auth.get_token()
        self.assertTrue(id_token)

        dataset, _ = auth.get_dataset('myList')
        self.assertTrue(dataset)

        # Test disabled since it would cause locks due to all the CI tests changing this at the same time.

        # # Python 2.7 doesn't support .timestamp(), and windows doesn't do '%s', so we need to calculate it ourself
        # epoch = datetime(1970, 1, 1, tzinfo=dateutil.tz.gettz('UTC'))
        # now = datetime.now(tz=dateutil.tz.gettz('UTC'))
        # timestamp = str(int((now - epoch).total_seconds())) + '000'
        # new_dataset = [
        #     {'id': '06e209f9-092e-421e-9499-58c62c292b98', 'timestamp': timestamp},
        #     {'id': 'da584be3-dea6-49c7-bfbd-c480d8096937', 'timestamp': timestamp}
        # ]
        #
        # auth.put_dataset('myList', new_dataset, sync_info)


if __name__ == '__main__':
    unittest.main()
