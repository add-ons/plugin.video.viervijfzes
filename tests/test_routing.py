# -*- coding: utf-8 -*-
""" Tests for Routing """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from resources.lib import addon


routing = addon.routing  # pylint: disable=invalid-name


class TestRouting(unittest.TestCase):
    """ Tests for Routing """

    def __init__(self, *args, **kwargs):
        super(TestRouting, self).__init__(*args, **kwargs)

    def setUp(self):
        # Don't warn that we don't close our HTTPS connections, this is on purpose.
        # warnings.simplefilter("ignore", ResourceWarning)
        pass

    def test_main_menu(self):
        routing.run([routing.url_for(addon.show_main_menu), '0', ''])

    def test_channels_menu(self):
        routing.run([routing.url_for(addon.show_channels), '0', ''])
        routing.run([routing.url_for(addon.show_channel_menu, channel='Play4'), '0', ''])

    def test_catalog_menu(self):
        routing.run([routing.url_for(addon.show_catalog), '0', ''])

    def test_catalog_channel_menu(self):
        routing.run([routing.url_for(addon.show_channel_catalog, channel='Play4'), '0', ''])

    def test_catalog_program_menu(self):
        routing.run([routing.url_for(addon.show_catalog_program, channel='Play4', program='de-mol'), '0', ''])

    def test_catalog_program_season_menu(self):
        routing.run([routing.url_for(addon.show_catalog_program_season, channel='Play4', program='de-mol', season=-1), '0', ''])

    def test_search_menu(self):
        routing.run([routing.url_for(addon.show_search), '0', ''])
        routing.run([routing.url_for(addon.show_search, query='de mol'), '0', ''])

    def test_tvguide_menu(self):
        routing.run([routing.url_for(addon.show_channel_tvguide, channel='Play4'), '0', ''])
        routing.run([routing.url_for(addon.show_channel_tvguide_detail, channel='Play4', date='today'), '0', ''])


if __name__ == '__main__':
    unittest.main()
