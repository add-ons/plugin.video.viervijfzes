# -*- coding: utf-8 -*-
""" AUTH API """

from __future__ import absolute_import, division, unicode_literals

import html
import json
import logging
import re

import requests

from resources.lib.sbs import CHANNELS

_LOGGER = logging.getLogger('api')


class Program:
    """ Defines a Program. """

    def __init__(self, uuid=None, path=None, channel=None, title=None, description=None, cover=None, background=None, seasons=None, episodes=None):
        """
        :type uuid: str
        :type path: str
        :type channel: str
        :type title: str
        :type description: str
        :type cover: str
        :type background: str
        :type seasons: list[Season]
        :type episodes: list[Episode]
        """
        self.uuid = uuid
        self.path = path
        self.channel = channel
        self.title = title
        self.description = description
        self.cover = cover
        self.background = background
        self.seasons = seasons
        self.episodes = episodes

    def __repr__(self):
        return "%r" % self.__dict__


class Season:
    """ Defines a Season. """

    def __init__(self, uuid=None, path=None, channel=None, title=None, description=None, cover=None, number=None):
        """
        :type uuid: str
        :type path: str
        :type channel: str
        :type title: str
        :type description: str
        :type cover: str
        :type number: int

        """
        self.uuid = uuid
        self.path = path
        self.channel = channel
        self.title = title
        self.description = description
        self.cover = cover
        self.number = number

    def __repr__(self):
        return "%r" % self.__dict__


class Episode:
    """ Defines an Episode. """

    def __init__(self, uuid=None, path=None, channel=None, title=None, description=None, cover=None, duration=None, season=None, number=None):
        """
        :type uuid: str
        :type path: str
        :type channel: str
        :type title: str
        :type description: str
        :type cover: str
        :type duration: int
        :type season: int
        :type number: int
        """
        self.uuid = uuid
        self.path = path
        self.channel = channel
        self.title = title
        self.description = description
        self.cover = cover
        self.duration = duration
        self.season = season
        self.number = number

    def __repr__(self):
        return "%r" % self.__dict__


class ContentApi:
    """ Vier/Vijf/Zes Content API"""
    API_ENDPOINT = 'https://api.viervijfzes.be'

    def __init__(self, token):
        """ Initialise object """
        self._token = token

        self._session = requests.session()
        self._session.headers['authorization'] = token

    def get_notifications(self):
        """ Get a list of notifications for your account. """
        response = self._get_url(self.API_ENDPOINT + '/notifications')
        data = json.loads(response)
        return data

    def get_stream(self, uuid):
        """ Get the stream URL to use for this video. """
        response = self._get_url(self.API_ENDPOINT + '/content/%s' % uuid)
        data = json.loads(response)
        return data['video']['S']

    def get_programs(self, channel):
        """ Get a list of all programs of the specified channel.
            NOTE: This function doesn't use an API. """
        if channel not in CHANNELS:
            raise Exception('Unknown channel %s' % channel)

        # Load webpage
        data = self._get_url(CHANNELS[channel]['url'])

        # Parse programs
        regex_programs = re.compile(r'<a class="program-overview__link" href="(?P<path>[^"]+)">\s+'
                                    r'<span class="program-overview__title">\s+(?P<title>[^<]+)</span>.*?'
                                    r'</a>', re.DOTALL)

        programs = [
            Program(channel=channel,
                    path=program.group('path').lstrip('/'),
                    title=program.group('title').strip())
            for program in regex_programs.finditer(data)
        ]

        return programs

    def get_program(self, channel, path):
        """ Get a Program object from the specified page.
            NOTE: This function doesn't use an API. """
        if channel not in CHANNELS:
            raise Exception('Unknown channel %s' % channel)

        # Load webpage
        page = self._get_url(CHANNELS[channel]['url'] + '/' + path)

        # Extract JSON
        regex_program = re.compile(r'data-hero="([^"]+)', re.DOTALL)
        json_data = html.unescape(regex_program.search(page).group(1))

        data = json.loads(json_data)['data']

        # Create Program info
        program = Program(
            uuid=data['id'],
            path=path,
            channel=channel,
            title=data['title'],
            description=data['description'],
            cover=data['images']['poster'],
            background=data['images']['hero'],
        )

        # Create Season info
        program.seasons = [
            Season(
                uuid=playlist['id'],
                path=playlist['link'].lstrip('/'),
                channel=channel,
                title=playlist['title'],
                number=playlist['episodes'][0]['seasonNumber'],  # You did not see this
            )
            for playlist in data['playlists']
        ]

        # Create Episodes info
        program.episodes = [
            Episode(
                uuid=episode['videoUuid'],
                path=episode['link'].lstrip('/'),
                channel=channel,
                title=episode['title'],
                description=episode['pageInfo']['description'],
                cover=episode['image'],
                duration=episode['duration'],
                season=episode['seasonNumber'],
                number=episode['episodeNumber'],
                # TODO: add unpublishDate as expiry
            )
            for playlist in data['playlists']
            for episode in playlist['episodes']
        ]

        return program

    def get_episode(self, channel, path):
        """ Get a Episode object from the specified page.
            NOTE: This function doesn't use an API. """
        # TODO: fetch page and parse out a Episode
        raise NotImplementedError()

    def _get_url(self, url, params=None):
        """ Makes a GET request for the specified URL.
        :type url: str
        :rtype str
        """
        response = self._session.get(url, params=params)

        # TODO: handle errors
        return response.text
