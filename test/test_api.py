# -*- coding: utf-8 -*-
""" Tests for Content API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

from resources.lib import kodiutils
from resources.lib.viervijfzes.auth import AuthApi
from resources.lib.viervijfzes.content import ContentApi, Program, Episode

_LOGGER = logging.getLogger('test-api')


class TestApi(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestApi, self).__init__(*args, **kwargs)
        self._auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())

    def test_notifications(self):
        api = ContentApi(self._auth.get_token())
        notifications = api.get_notifications()
        self.assertIsInstance(notifications, list)

    def test_programs(self):
        api = ContentApi(self._auth.get_token())

        for channel in ['vier', 'vijf', 'zes']:
            channels = api.get_programs(channel)
            self.assertIsInstance(channels, list)

    def test_episodes(self):
        api = ContentApi(self._auth.get_token())

        for channel, program in [('vier', 'auwch'), ('vijf', 'zo-man-zo-vrouw')]:
            program = api.get_program(channel, program)
            self.assertIsInstance(program, Program)
            self.assertIsInstance(program.seasons, dict)
            # self.assertIsInstance(program.seasons[0], Season)
            self.assertIsInstance(program.episodes, list)
            self.assertIsInstance(program.episodes[0], Episode)
            _LOGGER.info('Got program: %s', program)

    def test_get_stream(self):
        api = ContentApi(self._auth.get_token())
        program = api.get_program('vier', 'auwch')
        episode = program.episodes[0]
        video = api.get_stream(episode.channel, episode.uuid)
        self.assertTrue(video)

        _LOGGER.info('Got video URL: %s', video)


if __name__ == '__main__':
    unittest.main()
