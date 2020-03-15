# -*- coding: utf-8 -*-
""" EPG API """

from __future__ import absolute_import, division, unicode_literals

import json
import logging
from datetime import datetime

import requests

_LOGGER = logging.getLogger('epg')


class EpgProgram:
    def __init__(self, program_title, episode_title, episode_title_original, nr, season, genre, start, won_id, won_program_id, program_description, plot,
                 duration, program_url, video_url, cover):
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
    EPG_ENDPOINTS = {
        'vier': 'https://www.vier.be/api/epg/{date}',
        'vijf': 'https://www.vijf.be/api/epg/{date}',
        'zes': 'https://www.zestv.be/api/epg/{date}',
    }

    URL_ENDPOINTS = {
        'vier': 'https://www.vier.be{path}',
        'vijf': 'https://www.vijf.be{path}',
        'zes': 'https://www.zestv.be{path}',
    }

    def __init__(self):
        """ Initialise object """

    def get_epg(self, channel, date):
        """ Returns an authentication token """
        if channel not in self.EPG_ENDPOINTS:
            raise Exception('Unknown channel %s' % channel)

        # Request the epg data
        response = self._get_url(self.EPG_ENDPOINTS.get(channel).format(date=date))
        data = json.loads(response)

        # Parse the results
        return [self._parse_program(channel, x) for x in data]

    def _parse_program(self, channel, data) -> EpgProgram:
        """ Parse the epg json data to a EpgProgram object. """

        # Return a mapping to a generic EpgProgram
        return EpgProgram(
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
            program_url=self.URL_ENDPOINTS[channel].format(path=data.get('program_node', {}).get('url')),
            video_url=self.URL_ENDPOINTS[channel].format(path=data.get('video_node', {}).get('url')),
            cover=data.get('video_node', {}).get('image'),
        )

    def _get_url(self, url):
        """ Makes a GET request for the specified URL.
        :type url: str
        :rtype str
        """
        response = requests.get(url)

        # TODO check error code

        return response.text
