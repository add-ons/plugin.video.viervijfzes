# -*- coding: utf-8 -*-
""" EPG API """

from __future__ import absolute_import, division, unicode_literals

import json
import logging
from datetime import datetime, timedelta

import dateutil
import requests

from resources.lib import kodiutils

_LOGGER = logging.getLogger('epg-api')


class EpgProgram:
    """ Defines a Program in the EPG. """

    def __init__(self, channel, program_title, episode_title, episode_title_original, nr, season, genre, start, won_id, won_program_id, program_description,
                 description, duration, program_url, video_url, cover, airing):
        self.channel = channel
        self.program_title = program_title
        self.episode_title = episode_title
        self.episode_title_original = episode_title_original
        self.nr = nr
        self.season = season
        self.genre = genre
        self.start = start
        self.won_id = won_id
        self.won_program_id = won_program_id
        self.program_description = program_description
        self.description = description
        self.duration = duration
        self.program_url = program_url
        self.video_url = video_url
        self.cover = cover
        self.airing = airing

    def __repr__(self):
        return "%r" % self.__dict__


class EpgApi:
    """ Vier/Vijf/Zes EPG API """

    EPG_ENDPOINTS = {
        'vier': 'https://www.vier.be/api/epg/{date}',
        'vijf': 'https://www.vijf.be/api/epg/{date}',
        'zes': 'https://www.zestv.be/api/epg/{date}',
    }

    def __init__(self):
        """ Initialise object """
        self._session = requests.session()

    def get_epg(self, channel, date):
        """ Returns the EPG for the specified channel and date.
        :type channel: str
        :type date: str
        :rtype list[EpgProgram]
         """
        if channel not in self.EPG_ENDPOINTS:
            raise Exception('Unknown channel %s' % channel)

        if date is None:
            # Fetch today when no date is specified
            date = datetime.today().strftime('%Y-%m-%d')
        elif date == 'yesterday':
            date = (datetime.today() + timedelta(days=-1)).strftime('%Y-%m-%d')
        elif date == 'today':
            date = datetime.today().strftime('%Y-%m-%d')
        elif date == 'tomorrow':
            date = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

        # Request the epg data
        response = self._get_url(self.EPG_ENDPOINTS.get(channel).format(date=date))
        data = json.loads(response)

        # Parse the results
        return [self._parse_program(channel, x) for x in data]

    def get_dates(self, date_format):
        """ Return a dict of dates.
        :rtype: list[dict]
        """
        dates = []
        today = datetime.today()

        # The API provides 7 days in the past and 13 days in the future
        for i in range(-7, 13):
            day = today + timedelta(days=i)

            if i == -1:
                dates.append({
                    'title': '%s, %s' % (kodiutils.localize(30301), day.strftime(date_format)),  # Yesterday
                    'key': 'yesterday',
                    'date': day.strftime('%d.%m.%Y'),
                    'highlight': False,
                })
            elif i == 0:
                dates.append({
                    'title': '%s, %s' % (kodiutils.localize(30302), day.strftime(date_format)),  # Today
                    'key': 'today',
                    'date': day.strftime('%d.%m.%Y'),
                    'highlight': True,
                })
            elif i == 1:
                dates.append({
                    'title': '%s, %s' % (kodiutils.localize(30303), day.strftime(date_format)),  # Tomorrow
                    'key': 'tomorrow',
                    'date': day.strftime('%d.%m.%Y'),
                    'highlight': False,
                })
            else:
                dates.append({
                    'title': day.strftime(date_format),
                    'key': day.strftime('%Y-%m-%d'),
                    'date': day.strftime('%d.%m.%Y'),
                    'highlight': False,
                })

        return dates

    @staticmethod
    def _parse_program(channel, data):
        """ Parse the EPG JSON data to a EpgProgram object.
        :type channel: str
        :type data: dict
        :rtype EpgProgram
        """
        duration = int(data.get('duration')) if data.get('duration') else None

        # Check if this broadcast is currently airing
        timestamp = datetime.now()
        start = datetime.fromtimestamp(data.get('timestamp'))
        if duration:
            airing = bool(start <= timestamp < (start + timedelta(seconds=duration)))
        else:
            airing = False

        return EpgProgram(
            channel=channel,
            program_title=data.get('program_title'),
            episode_title=data.get('episode_title'),
            episode_title_original=data.get('original_title'),
            nr=int(data.get('episode_nr')) if data.get('episode_nr') else None,
            season=int(data.get('season')) if data.get('season') else None,
            genre=data.get('genre'),
            start=start,
            won_id=int(data.get('won_id')) if data.get('won_id') else None,
            won_program_id=int(data.get('won_program_id')) if data.get('won_program_id') else None,
            program_description=data.get('program_concept'),
            description=data.get('content_episode'),
            duration=duration,
            program_url=(data.get('program_node', {}).get('url') or '').lstrip('/'),
            video_url=(data.get('video_node', {}).get('url') or '').lstrip('/'),
            cover=data.get('video_node', {}).get('image'),
            airing=airing,
        )

    def get_broadcast(self, channel, timestamp):
        """ Load EPG information for the specified channel and date.
        :type channel: str
        :type timestamp: str
        :rtype: EpgProgram
        """
        # Parse to a real datetime
        timestamp = dateutil.parser.parse(timestamp)

        # Load guide info for this date
        programs = self.get_epg(channel=channel, date=timestamp.strftime('%Y-%m-%d'))

        # Find a matching broadcast
        for broadcast in programs:
            if timestamp <= broadcast.start < (broadcast.start + timedelta(seconds=broadcast.duration)):
                return broadcast

        return None

    def _get_url(self, url):
        """ Makes a GET request for the specified URL.
        :type url: str
        :rtype str
        """
        response = self._session.get(url)

        # TODO check error code

        return response.text
