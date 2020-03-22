# -*- coding: utf-8 -*-
""" Tests for EPG API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest
from datetime import date

from resources.lib import kodiutils
from resources.lib.viervijfzes.auth import AuthApi
from resources.lib.viervijfzes.content import ContentApi, Episode
from resources.lib.viervijfzes.epg import EpgApi, EpgProgram

_LOGGER = logging.getLogger('test-epg')


class TestEpg(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestEpg, self).__init__(*args, **kwargs)
        self._epg = EpgApi()

    def test_vier_today(self):
        programs = self._epg.get_epg('vier', date.today().strftime('%Y-%m-%d'))
        self.assertIsInstance(programs, list)
        self.assertIsInstance(programs[0], EpgProgram)

    def test_vijf_today(self):
        programs = self._epg.get_epg('vijf', date.today().strftime('%Y-%m-%d'))
        self.assertIsInstance(programs, list)
        self.assertIsInstance(programs[0], EpgProgram)

    def test_zes_today(self):
        programs = self._epg.get_epg('zes', date.today().strftime('%Y-%m-%d'))
        self.assertIsInstance(programs, list)
        self.assertIsInstance(programs[0], EpgProgram)

    def test_unknown_today(self):
        with self.assertRaises(Exception):
            self._epg.get_epg('vtm', date.today().strftime('%Y-%m-%d'))

    def test_vier_out_of_range(self):
        programs = self._epg.get_epg('vier', '2020-01-01')
        self.assertEqual(programs, [])

    def test_play_video_from_epg(self):
        epg_programs = self._epg.get_epg('vier', date.today().strftime('%Y-%m-%d'))
        epg_program = [program for program in epg_programs if program.video_url][0]

        auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'))
        api = ContentApi(auth)

        # Lookup the Episode data since we don't have an UUID
        episode = api.get_episode(epg_program.channel, epg_program.video_url)
        self.assertIsInstance(episode, Episode)

        # Get stream based on the Episode's UUID
        video = api.get_stream_by_uuid(episode.uuid)
        self.assertTrue(video)


if __name__ == '__main__':
    unittest.main()
