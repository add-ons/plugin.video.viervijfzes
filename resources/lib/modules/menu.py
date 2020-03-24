# -*- coding: utf-8 -*-
""" Menu module """

from __future__ import absolute_import, division, unicode_literals

from resources.lib import kodiutils
from resources.lib.kodiutils import TitleItem
from resources.lib.viervijfzes import CHANNELS, STREAM_DICT
from resources.lib.viervijfzes.content import Program, Episode


class Menu:
    """ Menu code """

    def __init__(self):
        """ Initialise object """

    @staticmethod
    def show_mainmenu():
        """ Show the main menu """
        listing = [
            TitleItem(
                title=kodiutils.localize(30001),  # A-Z
                path=kodiutils.url_for('show_catalog'),
                art_dict=dict(
                    icon='DefaultMovieTitle.png',
                    fanart=kodiutils.get_addon_info('fanart'),
                ),
                info_dict=dict(
                    plot=kodiutils.localize(30002),
                )
            ),
            TitleItem(
                title=kodiutils.localize(30007),  # TV Channels
                path=kodiutils.url_for('show_channels'),
                art_dict=dict(
                    icon='DefaultAddonPVRClient.png',
                    fanart=kodiutils.get_addon_info('fanart'),
                ),
                info_dict=dict(
                    plot=kodiutils.localize(30008),
                )
            ),
            TitleItem(
                title=kodiutils.localize(30009),  # Search
                path=kodiutils.url_for('show_search'),
                art_dict=dict(
                    icon='DefaultAddonsSearch.png',
                    fanart=kodiutils.get_addon_info('fanart'),
                ),
                info_dict=dict(
                    plot=kodiutils.localize(30010),
                )
            )
        ]

        kodiutils.show_listing(listing, sort=['unsorted'])

    @staticmethod
    def generate_titleitem(item):
        """ Generate a TitleItem based on a Program or Episode.
        :type item: Union[Program, Episode]
        :rtype TitleItem
        """
        art_dict = {
            'thumb': item.cover,
            'cover': item.cover,
        }
        info_dict = {
            'title': item.title,
            'plot': item.description,
            'studio': CHANNELS.get(item.channel, {}).get('studio_icon'),
            'aired': item.aired.strftime('%Y-%m-%d') if item.aired else None,
        }
        prop_dict = {}

        #
        # Program
        #
        if isinstance(item, Program):
            art_dict.update({
                'fanart': item.background,
            })
            info_dict.update({
                'mediatype': None,
                'season': len(item.seasons) if item.seasons else None,
            })

            if isinstance(item.episodes, list) and not item.episodes:
                # We know that we don't have episodes
                title = '[COLOR gray]' + item.title + '[/COLOR]'
            else:
                # We have episodes, or we don't know it
                title = item.title

            return TitleItem(title=title,
                             path=kodiutils.url_for('show_catalog_program', channel=item.channel, program=item.path),
                             art_dict=art_dict,
                             info_dict=info_dict)

        #
        # Episode
        #
        if isinstance(item, Episode):
            art_dict.update({
                'fanart': item.cover,
            })
            info_dict.update({
                'mediatype': 'episode',
                'tvshowtitle': item.program_title,
                'duration': item.duration,
                'season': item.season,
                'episode': item.number,
            })

            stream_dict = STREAM_DICT.copy()
            stream_dict.update({
                'duration': item.duration,
            })

            return TitleItem(title=info_dict['title'],
                             path=kodiutils.url_for('play', uuid=item.uuid),
                             art_dict=art_dict,
                             info_dict=info_dict,
                             stream_dict=stream_dict,
                             prop_dict=prop_dict,
                             is_playable=True)

        raise Exception('Unknown video_type')
