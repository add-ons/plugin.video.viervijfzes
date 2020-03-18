# -*- coding: utf-8 -*-
""" Tests for EPG API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
from datetime import date

import six

from resources.lib import kodiutils
from resources.lib.viervijfzes.auth import AuthApi
from resources.lib.viervijfzes.content import ContentApi, Episode
from resources.lib.viervijfzes.epg import EpgApi, EpgProgram


class TestEpg(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestEpg, self).__init__(*args, **kwargs)
        self._auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())

    def test_vier_today(self):
        epg = EpgApi()
        programs = epg.get_epg('vier', date.today().strftime('%Y-%m-%d'))
        self.assertIsInstance(programs, list)
        self.assertIsInstance(programs[0], EpgProgram)

    def test_vijf_today(self):
        epg = EpgApi()
        programs = epg.get_epg('vijf', date.today().strftime('%Y-%m-%d'))
        self.assertIsInstance(programs, list)
        self.assertIsInstance(programs[0], EpgProgram)

    def test_zes_today(self):
        epg = EpgApi()
        programs = epg.get_epg('zes', date.today().strftime('%Y-%m-%d'))
        self.assertIsInstance(programs, list)
        self.assertIsInstance(programs[0], EpgProgram)

    def test_unknown_today(self):
        epg = EpgApi()
        with self.assertRaises(Exception):
            epg.get_epg('vtm', date.today().strftime('%Y-%m-%d'))

    def test_vier_out_of_range(self):
        epg = EpgApi()
        programs = epg.get_epg('vier', '2020-01-01')
        self.assertEqual(programs, [])

    def test_play_video_from_epg(self):
        epg = EpgApi()
        epg_programs = epg.get_epg('vier', date.today().strftime('%Y-%m-%d'))
        epg_program = [program for program in epg_programs if program.video_url][0]

        # Lookup the Episode data since we don't have an UUID
        api = ContentApi(self._auth.get_token())
        episode = api.get_episode(epg_program.channel, epg_program.video_url)
        self.assertIsInstance(episode, Episode)

        # Get stream based on the Episode's UUID
        video = api.get_stream(episode.channel, episode.uuid)
        self.assertTrue(video)


if __name__ == '__main__':
    unittest.main()
