# -*- coding: utf-8 -*-
""" EPG API """

from __future__ import absolute_import, division, unicode_literals

import json
import logging
from datetime import datetime

import requests

_LOGGER = logging.getLogger('epg')


class EpgProgram:
    """ Defines a Program in the EPG. """

    def __init__(self, channel, program_title, episode_title, episode_title_original, nr, season, genre, start, won_id, won_program_id, program_description,
                 plot, duration, program_url, video_url, cover):
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
        self.plot = plot
        self.duration = duration
        self.program_url = program_url
        self.video_url = video_url
        self.cover = cover

    def __repr__(self):
        return "%r" % self.__dict__


class SbsEpg:
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
         """
        if channel not in self.EPG_ENDPOINTS:
            raise Exception('Unknown channel %s' % channel)

        # Request the epg data
        response = self._get_url(self.EPG_ENDPOINTS.get(channel).format(date=date))
        data = json.loads(response)

        # Parse the results
        return [self._parse_program(channel, x) for x in data]

    @staticmethod
    def _parse_program(channel, data):
        """ Parse the EPG JSON data to a EpgProgram object.
        :type channel: str
        :type data: dict
        :rtype EpgProgram
        """
        return EpgProgram(
            channel=channel,
            program_title=data.get('program_title'),
            episode_title=data.get('episode_title'),
            episode_title_original=data.get('original_title'),
            nr=int(data.get('episode_nr')) if data.get('episode_nr') else None,
            season=int(data.get('season')) if data.get('season') else None,
            genre=data.get('genre'),
            start=datetime.fromtimestamp(data.get('timestamp')),
            won_id=int(data.get('won_id')) if data.get('won_id') else None,
            won_program_id=int(data.get('won_program_id')) if data.get('won_program_id') else None,
            program_description=data.get('program_concept'),
            plot=data.get('content_episode'),
            duration=int(data.get('duration')) if data.get('duration') else None,
            program_url=(data.get('program_node', {}).get('url') or '').lstrip('/'),
            video_url=(data.get('video_node', {}).get('url') or '').lstrip('/'),
            cover=data.get('video_node', {}).get('image'),
        )

    def _get_url(self, url):
        """ Makes a GET request for the specified URL.
        :type url: str
        :rtype str
        """
        response = self._session.get(url)

        # TODO check error code

        return response.text
