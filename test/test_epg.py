# -*- coding: utf-8 -*-
""" Tests for EPG API """

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
from datetime import date

from resources.lib.sbs.epg import SbsEpg, EpgProgram


class TestEpg(unittest.TestCase):
    """ Tests for EPG API """

    def __init__(self, *args, **kwargs):
        super(TestEpg, self).__init__(*args, **kwargs)

    def test_vier_today(self):
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


if __name__ == '__main__':
    unittest.main()
