# -*- coding: utf-8 -*-
""" Menu code related to channels """

from __future__ import absolute_import, division, unicode_literals

import logging

from resources.lib import kodiutils
from resources.lib.kodiutils import TitleItem
from resources.lib.viervijfzes.content import UnavailableException
from resources.lib.viervijfzes.epg import EpgApi

try:  # Python 3
    from urllib.parse import quote
except ImportError:  # Python 2
    from urllib import quote

_LOGGER = logging.getLogger('tvguide')


class TvGuide:
    """ Menu code related to the TV Guide """

    def __init__(self):
        """ Initialise object """
        self._epg = EpgApi()

    def show_tvguide_channel(self, channel):
        """ Shows the dates in the tv guide
        :type channel: str
        """
        listing = []
        for day in self._epg.get_dates('%A %d %B %Y'):
            if day.get('highlight'):
                title = '[B]{title}[/B]'.format(title=day.get('title'))
            else:
                title = day.get('title')

            listing.append(
                TitleItem(title=title,
                          path=kodiutils.url_for('show_tvguide_detail', channel=channel, date=day.get('key')),
                          art_dict={
                              'icon': 'DefaultYear.png',
                              'thumb': 'DefaultYear.png',
                          },
                          info_dict={
                              'plot': None,
                              'date': day.get('date'),
                          })
            )

        kodiutils.show_listing(listing, 30013, content='files', sort=['date'])

    def show_tvguide_detail(self, channel=None, date=None):
        """ Shows the programs of a specific date in the tv guide
        :type channel: str
        :type date: str
        """
        try:
            programs = self._epg.get_epg(channel=channel, date=date)
        except UnavailableException as ex:
            kodiutils.notification(message=str(ex))
            kodiutils.end_of_directory()
            return

        listing = []
        for program in programs:
            # if broadcast.playable_type == 'episodes':
            #     context_menu = [(
            #         kodiutils.localize(30102),  # Go to Program
            #         'Container.Update(%s)' %
            #         kodiutils.url_for('show_catalog_program', channel=channel, program=broadcast.program_uuid)
            #     )]
            # else:
            #     context_menu = None

            title = '{time} - {title}{live}'.format(
                time=program.start.strftime('%H:%M'),
                title=program.program_title,
                live=' [I](LIVE)[/I]' if False else ''
            )

            if program.airing:
                title = '[B]{title}[/B]'.format(title=title)

            if program.video_url:
                path = kodiutils.url_for('play_from_page', channel=channel, item=quote(program.video_url, safe=''))
            else:
                path = None
                title = '[COLOR gray]' + title + '[/COLOR]'

            listing.append(
                TitleItem(title=title,
                          path=path,
                          art_dict={
                              'icon': program.cover,
                              'thumb': program.cover,
                          },
                          info_dict={
                              'title': title,
                              'plot': program.description,
                              'duration': program.duration,
                              'mediatype': 'video',
                          },
                          stream_dict={
                              'duration': program.duration,
                              'codec': 'h264',
                              'height': 1080,
                              'width': 1920,
                          },
                          # context_menu=context_menu,
                          is_playable=True)
            )

        kodiutils.show_listing(listing, 30013, content='episodes', sort=['unsorted'])

    def play_epg_datetime(self, channel, timestamp):
        """ Play a program based on the channel and the timestamp when it was aired
        :type channel: str
        :type timestamp: str
        """
        broadcast = self._epg.get_broadcast(channel, timestamp)
        if not broadcast:
            kodiutils.ok_dialog(heading=kodiutils.localize(30711), message=kodiutils.localize(30713))  # The requested video was not found in the guide.
            kodiutils.end_of_directory()
            return

        kodiutils.container_update(
            kodiutils.url_for('play', channel=channel, item=broadcast.video_url))
