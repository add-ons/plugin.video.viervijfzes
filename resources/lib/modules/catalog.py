# -*- coding: utf-8 -*-
""" Catalog module """

from __future__ import absolute_import, division, unicode_literals

import logging

from resources.lib import kodiutils
from resources.lib.kodiutils import TitleItem
from resources.lib.modules.menu import Menu
from resources.lib.viervijfzes import CHANNELS
from resources.lib.viervijfzes.auth import AuthApi
from resources.lib.viervijfzes.content import CACHE_PREVENT, ContentApi, UnavailableException

_LOGGER = logging.getLogger(__name__)


class Catalog:
    """ Menu code related to the catalog """

    def __init__(self):
        """ Initialise object """
        auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())
        self._api = ContentApi(auth, cache_path=kodiutils.get_cache_path())

    def show_catalog(self):
        """ Show all the programs of all channels """
        try:
            items = self._api.get_programs()
        except Exception as ex:
            kodiutils.notification(message=str(ex))
            raise

        listing = [Menu.generate_titleitem(item) for item in items]

        # Sort items by title
        # Used for A-Z listing or when movies and episodes are mixed.
        kodiutils.show_listing(listing, 30003, content='tvshows', sort='title')

    def show_catalog_channel(self, channel):
        """ Show the programs of a specific channel
        :type channel: str
        """
        try:
            items = self._api.get_programs(channel)
        except Exception as ex:
            kodiutils.notification(message=str(ex))
            raise

        listing = []
        for item in items:
            listing.append(Menu.generate_titleitem(item))

        # Sort items by title
        # Used for A-Z listing or when movies and episodes are mixed.
        kodiutils.show_listing(listing, 30003, content='tvshows', sort='title')

    def show_program(self, program_id):
        """ Show a program from the catalog
        :type program_id: str
         """
        try:
            program = self._api.get_program(program_id, extract_clips=True, cache=CACHE_PREVENT)  # Use CACHE_PREVENT since we want fresh data
        except UnavailableException:
            kodiutils.ok_dialog(message=kodiutils.localize(30717))  # This program is not available in the catalogue.
            kodiutils.end_of_directory()
            return

        if not program.episodes and not program.clips:
            kodiutils.ok_dialog(message=kodiutils.localize(30717))  # This program is not available in the catalogue.
            kodiutils.end_of_directory()
            return

        # Go directly to the season when we have only one season and no clips
        if not program.clips and len(program.seasons) == 1:
            self.show_program_season(program_id, list(program.seasons.values())[0].uuid)
            return

        studio = CHANNELS.get(program.channel, {}).get('studio_icon')

        listing = []

        # Add an '* All seasons' entry when configured in Kodi
        if program.seasons and kodiutils.get_global_setting('videolibrary.showallitems') is True:
            listing.append(
                TitleItem(
                    title='* %s' % kodiutils.localize(30204),  # * All seasons
                    path=kodiutils.url_for('show_catalog_program_season', program=program_id, season='-1'),
                    art_dict={
                        'fanart': program.background,
                    },
                    info_dict={
                        'tvshowtitle': program.title,
                        'title': kodiutils.localize(30204),  # All seasons
                        'plot': program.description,
                        'set': program.title,
                        'studio': studio,
                    }
                )
            )

        # Add the seasons
        for season in list(program.seasons.values()):
            listing.append(
                TitleItem(
                    title=season.title,  # kodiutils.localize(30205, season=season.number),  # Season {season}
                    path=kodiutils.url_for('show_catalog_program_season', program=program_id, season=season.uuid),
                    art_dict={
                        'fanart': program.background,
                    },
                    info_dict={
                        'tvshowtitle': program.title,
                        'title': kodiutils.localize(30205, season=season.number),  # Season {season}
                        'plot': season.description,
                        'set': program.title,
                        'studio': studio,
                    }
                )
            )

        # Add Clips
        if program.clips:
            listing.append(
                TitleItem(
                    title=kodiutils.localize(30059, program=program.title),  # Clips for {program}
                    path=kodiutils.url_for('show_catalog_program_clips', program=program_id),
                    art_dict={
                        'fanart': program.background,
                    },
                    info_dict={
                        'tvshowtitle': program.title,
                        'title': kodiutils.localize(30059, program=program.title),  # Clips for {program}
                        'plot': kodiutils.localize(30060, program=program.title),  # Watch short clips of {program}
                        'set': program.title,
                        'studio': studio,
                    }
                )
            )

        # Sort by label. Some programs return seasons unordered.
        kodiutils.show_listing(listing, 30003, content='tvshows')

    def show_program_season(self, program_id, season_uuid):
        """ Show the episodes of a program from the catalog
        :type program_id: str
        :type season_uuid: str
        """
        try:
            program = self._api.get_program(program_id)
        except UnavailableException:
            kodiutils.ok_dialog(message=kodiutils.localize(30717))  # This program is not available in the catalogue.
            kodiutils.end_of_directory()
            return

        if season_uuid == "-1":
            # Show all episodes
            episodes = program.episodes
        else:
            # Show the episodes of the season that was selected
            episodes = [e for e in program.episodes if e.season_uuid == season_uuid]

        listing = [Menu.generate_titleitem(episode) for episode in episodes]

        # Sort by episode number by default. Takes seasons into account.
        kodiutils.show_listing(listing, 30003, content='episodes', sort=['episode', 'duration'])

    def show_program_clips(self, program_id):
        """ Show the clips of a program from the catalog
        :type program_id: str
        """
        try:
            # We need to query the backend, since we don't cache clips.
            program = self._api.get_program(program_id, extract_clips=True, cache=CACHE_PREVENT)
        except UnavailableException:
            kodiutils.ok_dialog(message=kodiutils.localize(30717))  # This program is not available in the catalogue.
            kodiutils.end_of_directory()
            return

        listing = [Menu.generate_titleitem(episode) for episode in program.clips]

        # Sort like we get our results back.
        kodiutils.show_listing(listing, 30003, content='episodes')
