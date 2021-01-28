# -*- coding: utf-8 -*-
""" Channels module """

from __future__ import absolute_import, division, unicode_literals

import logging

from resources.lib import kodiutils
from resources.lib.kodiutils import TitleItem
from resources.lib.modules.menu import Menu
from resources.lib.viervijfzes import CHANNELS, STREAM_DICT
from resources.lib.viervijfzes.auth import AuthApi
from resources.lib.viervijfzes.content import CACHE_AUTO, CACHE_ONLY, ContentApi

_LOGGER = logging.getLogger(__name__)


class Channels:
    """ Menu code related to channels """

    def __init__(self):
        """ Initialise object """
        auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())
        self._api = ContentApi(auth, cache_path=kodiutils.get_cache_path())

    @staticmethod
    def show_channels():
        """ Shows TV channels """
        listing = []
        for i, key in enumerate(CHANNELS):  # pylint: disable=unused-variable
            channel = CHANNELS[key]

            # Lookup the high resolution logo based on the channel name
            icon = '{path}/resources/logos/{logo}'.format(path=kodiutils.addon_path(), logo=channel.get('logo'))
            fanart = '{path}/resources/logos/{logo}'.format(path=kodiutils.addon_path(), logo=channel.get('background'))

            context_menu = [
                (
                    kodiutils.localize(30053, channel=channel.get('name')),  # TV Guide for {channel}
                    'Container.Update(%s)' %
                    kodiutils.url_for('show_channel_tvguide', channel=channel.get('epg'))
                )
            ]

            listing.append(
                TitleItem(
                    title=channel.get('name'),
                    path=kodiutils.url_for('show_channel_menu', channel=key),
                    art_dict={
                        'icon': icon,
                        'thumb': icon,
                        'fanart': fanart,
                    },
                    info_dict={
                        'plot': None,
                        'playcount': 0,
                        'mediatype': 'video',
                    },
                    stream_dict=STREAM_DICT,
                    context_menu=context_menu
                ),
            )

        kodiutils.show_listing(listing, 30007)

    @staticmethod
    def show_channel_menu(channel):
        """ Shows a TV channel
        :type channel: str
        """
        channel_info = CHANNELS[channel]

        # Lookup the high resolution logo based on the channel name
        fanart = '{path}/resources/logos/{logo}'.format(path=kodiutils.addon_path(), logo=channel_info.get('background'))

        listing = []

        if channel_info.get('epg_id'):
            listing.append(
                TitleItem(
                    title=kodiutils.localize(30053, channel=channel_info.get('name')),  # TV Guide for {channel}
                    path=kodiutils.url_for('show_channel_tvguide', channel=channel),
                    art_dict={
                        'icon': 'DefaultAddonTvInfo.png',
                        'fanart': fanart,
                    },
                    info_dict={
                        'plot': kodiutils.localize(30054, channel=channel_info.get('name')),  # Browse the TV Guide for {channel}
                    }
                )
            )

        listing.append(
            TitleItem(
                title=kodiutils.localize(30055, channel=channel_info.get('name')),  # Catalog for {channel}
                path=kodiutils.url_for('show_channel_catalog', channel=channel),
                art_dict={
                    'icon': 'DefaultMovieTitle.png',
                    'fanart': fanart,
                },
                info_dict={
                    'plot': kodiutils.localize(30056, channel=channel_info.get('name')),  # Browse the Catalog for {channel}
                }
            )
        )

        # listing.append(
        #     TitleItem(
        #         title=kodiutils.localize(30057, channel=channel_info.get('name')),  # Categories for {channel}
        #         path=kodiutils.url_for('show_channel_categories', channel=channel),
        #         art_dict={
        #             'icon': 'DefaultGenre.png',
        #             'fanart': fanart,
        #         },
        #         info_dict={
        #             'plot': kodiutils.localize(30058, channel=channel_info.get('name')),  # Browse the Categories for {channel}
        #         }
        #     )
        # )

        # Add YouTube channels
        if kodiutils.get_cond_visibility('System.HasAddon(plugin.video.youtube)') != 0:
            for youtube in channel_info.get('youtube', []):
                listing.append(
                    TitleItem(
                        title=kodiutils.localize(30206, label=youtube.get('label')),  # Watch {label} on YouTube
                        path=youtube.get('path'),
                        info_dict={
                            'plot': kodiutils.localize(30206, label=youtube.get('label')),  # Watch {label} on YouTube
                        }
                    )
                )

        kodiutils.show_listing(listing, 30007, sort=['unsorted'])

    def show_channel_categories(self, channel):
        """ Shows the categories of a channel
        :type channel: str
        """
        categories = self._api.get_categories(channel)

        listing = [
            TitleItem(
                title=category.title,
                path=kodiutils.url_for('show_channel_category', channel=category.channel, category=category.uuid),
                art_dict={
                    'icon': 'DefaultGenre.png',
                },
            ) for category in categories
        ]

        kodiutils.show_listing(listing, 30007, sort=['unsorted'])

    def show_channel_category(self, channel, category_id):
        """ Shows a selected category of a channel
        :type channel: str
        :type category_id: str
        """
        categories = self._api.get_categories(channel)

        # Extract selected category
        category = next(category for category in categories if category.uuid == category_id)
        if not category:
            raise Exception('Unknown category')

        # Add programs
        listing_programs = []
        for item in category.programs:
            program = self._api.get_program(item.path, CACHE_ONLY)  # Get program details, but from cache only

            if program:
                listing_programs.append(Menu.generate_titleitem(program))
            else:
                listing_programs.append(Menu.generate_titleitem(item))

        # Add episodes
        listing_episodes = []
        for item in category.episodes:
            # We don't have the Program Name without making a request to the page, so we use CACHE_AUTO instead of CACHE_ONLY.
            # This will make a request for each item in this view (about 12 items), but it goes quite fast.
            # Results are cached, so this will only happen once.
            episode = self._api.get_episode(item.path, CACHE_AUTO)

            if episode:
                listing_episodes.append(Menu.generate_titleitem(episode))
            else:
                listing_episodes.append(Menu.generate_titleitem(item))

        kodiutils.show_listing(listing_programs + listing_episodes, 30007, content='tvshows', sort=['unsorted'])
