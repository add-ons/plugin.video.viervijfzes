# -*- coding: utf-8 -*-
""" Addon code """

from __future__ import absolute_import, division, unicode_literals

import logging

from routing import Plugin

from resources.lib import kodilogging

kodilogging.config()
routing = Plugin()  # pylint: disable=invalid-name
_LOGGER = logging.getLogger('addon')


@routing.route('/')
def show_main_menu():
    """ Show the main menu """
    from resources.lib.modules.menu import Menu
    Menu().show_mainmenu()


@routing.route('/channels')
def show_channels():
    """ Shows Live TV channels """
    from resources.lib.modules.channels import Channels
    Channels().show_channels()


@routing.route('/channels/<channel>')
def show_channel_menu(channel):
    """ Shows Live TV channels """
    from resources.lib.modules.channels import Channels
    Channels().show_channel_menu(channel)


@routing.route('/tvguide/channel/<channel>')
def show_tvguide_channel(channel):
    """ Shows the dates in the tv guide """
    from resources.lib.modules.tvguide import TvGuide
    TvGuide().show_tvguide_channel(channel)


@routing.route('/tvguide/channel/<channel>/<date>')
def show_tvguide_detail(channel=None, date=None):
    """ Shows the programs of a specific date in the tv guide """
    from resources.lib.modules.tvguide import TvGuide
    TvGuide().show_tvguide_detail(channel, date)


@routing.route('/catalog')
def show_catalog():
    """ Show the catalog """
    from resources.lib.modules.catalog import Catalog
    Catalog().show_catalog()


@routing.route('/catalog/by-channel/<channel>')
def show_catalog_channel(channel):
    """ Show a category in the catalog """
    from resources.lib.modules.catalog import Catalog
    Catalog().show_catalog_channel(channel)


@routing.route('/catalog/program/<channel>/<program>')
def show_catalog_program(channel, program):
    """ Show a program from the catalog """
    from resources.lib.modules.catalog import Catalog
    Catalog().show_program(channel, program)


@routing.route('/catalog/program/<channel>/<program>/<season>')
def show_catalog_program_season(channel, program, season):
    """ Show a program from the catalog """
    from resources.lib.modules.catalog import Catalog
    Catalog().show_program_season(channel, program, season)


@routing.route('/search')
@routing.route('/search/<query>')
def show_search(query=None):
    """ Shows the search dialog """
    from resources.lib.modules.search import Search
    Search().show_search(query)


@routing.route('/play/catalog/<uuid>')
def play(uuid):
    """ Play the requested item """
    from resources.lib.modules.player import Player
    Player().play(uuid)


@routing.route('/play/page/<channel>/<page>')
def play_from_page(channel, page):
    """ Play the requested item """
    try:  # Python 3
        from urllib.parse import unquote
    except ImportError:  # Python 2
        from urllib import unquote

    from resources.lib.modules.player import Player
    Player().play_from_page(channel, unquote(page))


@routing.route('/metadata/update')
def metadata_update():
    """ Update the metadata for the listings (called from settings) """
    from resources.lib.modules.metadata import Metadata
    Metadata().update()


@routing.route('/metadata/clean')
def metadata_clean():
    """ Clear metadata (called from settings) """
    from resources.lib.modules.metadata import Metadata
    Metadata().clean()


def run(params):
    """ Run the routing plugin """
    routing.run(params)
