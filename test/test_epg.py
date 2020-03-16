# -*- coding: utf-8 -*-
""" Tests for EPG API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import unittest
from datetime import date

from resources.lib.sbs.auth import SbsAuth
from resources.lib.sbs.epg import SbsEpg, EpgProgram


class TestEpg(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestEpg, self).__init__(*args, **kwargs)
        self._auth = SbsAuth(os.getenv('VVZ_USERNAME', ''), os.getenv('VVZ_PASSWORD', ''), cache='/tmp/viervijfzes-tokens.json')

    def test_vier_today(self):
        """ Test"""
        epg = SbsEpg()
        programs = epg.get_epg('vier', date.today().strftime('%Y-%m-%d'))
        self.assertIsInstance(programs, list)
        self.assertIsInstance(programs[0], EpgProgram)

    def test_vijf_today(self):
        epg = SbsEpg()
        programs = epg.get_epg('vijf', date.today().strftime('%Y-%m-%d'))
        self.assertIsInstance(programs, list)
        self.assertIsInstance(programs[0], EpgProgram)

    def test_zes_today(self):
        epg = SbsEpg()
        programs = epg.get_epg('zes', date.today().strftime('%Y-%m-%d'))
        self.assertIsInstance(programs, list)
        self.assertIsInstance(programs[0], EpgProgram)

    def test_unknown_today(self):
        epg = SbsEpg()
        with self.assertRaises(Exception):
            epg.get_epg('vtm', date.today().strftime('%Y-%m-%d'))

    def test_vier_out_of_range(self):
        epg = SbsEpg()
        programs = epg.get_epg('vier', '2020-01-01')
        self.assertEqual(programs, [])

    # def test_play_video(self):
    #     epg = SbsEpg()
    #     epg_programs = epg.get_epg('vier', date.today().strftime('%Y-%m-%d'))
    #     epg_program = [program for program in epg_programs if program.video_url][0]
    #
    #     api = SbsApi(self._auth.get_token())
    #     episode = api.get_episode(epg_program.channel, epg_program.video_url)
    #     self.assertIsInstance(Episode, episode)


if __name__ == '__main__':
    unittest.main()
