# -*- coding: utf-8 -*-
""" Channels module """

from __future__ import absolute_import, division, unicode_literals

import logging

from resources.lib import kodiutils
from resources.lib.kodiutils import TitleItem
from resources.lib.viervijfzes import CHANNELS, STREAM_DICT

_LOGGER = logging.getLogger('channels')


class Channels:
    """ Menu code related to channels """

    def __init__(self):
        """ Initialise object """

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
                    kodiutils.url_for('show_tvguide_channel', channel=channel.get('epg'))
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
                        'studio': channel.get('studio_icon'),
                    },
                    stream_dict=STREAM_DICT,
                    context_menu=context_menu
                ),
            )

        kodiutils.show_listing(listing, 30007)

    @staticmethod
    def show_channel_menu(key):
        """ Shows a TV channel
        :type key: str
        """
        channel = CHANNELS[key]

        # Lookup the high resolution logo based on the channel name
        fanart = '{path}/resources/logos/{logo}'.format(path=kodiutils.addon_path(), logo=channel.get('background'))

        listing = [
            TitleItem(
                title=kodiutils.localize(30053, channel=channel.get('name')),  # TV Guide for {channel}
                path=kodiutils.url_for('show_tvguide_channel', channel=key),
                art_dict={
                    'icon': 'DefaultAddonTvInfo.png',
                    'fanart': fanart,
                },
                info_dict={
                    'plot': kodiutils.localize(30054, channel=channel.get('name')),  # Browse the TV Guide for {channel}
                }
            ),
            TitleItem(
                title=kodiutils.localize(30055, channel=channel.get('name')),  # Catalog for {channel}
                path=kodiutils.url_for('show_catalog_channel', channel=key),
                art_dict={
                    'icon': 'DefaultMovieTitle.png',
                    'fanart': fanart,
                },
                info_dict={
                    'plot': kodiutils.localize(30056, channel=channel.get('name')),  # Browse the Catalog for {channel}
                }
            )
        ]

        # Add YouTube channels
        if kodiutils.get_cond_visibility('System.HasAddon(plugin.video.youtube)') != 0:
            for youtube in channel.get('youtube', []):
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
