# -*- coding: utf-8 -*-
""" Tests for Content API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

import resources.lib.kodiutils as kodiutils
from resources.lib.viervijfzes.auth import AuthApi
from resources.lib.viervijfzes.content import ContentApi, Program, Episode

_LOGGER = logging.getLogger('test-api')


class TestApi(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestApi, self).__init__(*args, **kwargs)
        auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'))
        self._api = ContentApi(auth)

    def test_programs(self):
        for channel in ['vier', 'vijf', 'zes']:
            programs = self._api.get_programs(channel)
            self.assertIsInstance(programs, list)
            self.assertIsInstance(programs[0], Program)

    def test_episodes(self):
        for channel, program in [('vier', 'auwch'), ('vijf', 'zo-man-zo-vrouw')]:
            program = self._api.get_program(channel, program)
            self.assertIsInstance(program, Program)
            self.assertIsInstance(program.seasons, dict)
            self.assertIsInstance(program.episodes, list)
            self.assertIsInstance(program.episodes[0], Episode)

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_get_stream(self):
        program = self._api.get_program('vier', 'auwch')
        self.assertIsInstance(program, Program)

        program_by_uuid = self._api.get_program_by_uuid(program.uuid)
        self.assertIsInstance(program_by_uuid, Program)

        episode = program.episodes[0]
        video = self._api.get_stream_by_uuid(episode.uuid)
        self.assertTrue(video)


if __name__ == '__main__':
    unittest.main()
