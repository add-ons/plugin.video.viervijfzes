# -*- coding: utf-8 -*-
""" AUTH API """

from __future__ import absolute_import, division, unicode_literals

import json
import logging
import re
from datetime import datetime

from six.moves.html_parser import HTMLParser
import requests

from resources.lib import kodiutils
from resources.lib.viervijfzes import CHANNELS

_LOGGER = logging.getLogger('content-api')

CACHE_AUTO = 1  # Allow to use the cache, and query the API if no cache is available
CACHE_ONLY = 2  # Only use the cache, don't use the API
CACHE_PREVENT = 3  # Don't use the cache


class UnavailableException(Exception):
    """ Is thrown when an item is unavailable. """


class NoContentException(Exception):
    """ Is thrown when no items are unavailable. """


class GeoblockedException(Exception):
    """ Is thrown when a geoblocked item is played. """


class Program:
    """ Defines a Program. """

    def __init__(self, uuid=None, path=None, channel=None, title=None, description=None, aired=None, cover=None, background=None, seasons=None, episodes=None):
        """
        :type uuid: str
        :type path: str
        :type channel: str
        :type title: str
        :type description: str
        :type aired: datetime
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
        self.aired = aired
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

    def __init__(self, uuid=None, nodeid=None, path=None, channel=None, program_title=None, title=None, description=None, cover=None, duration=None,
                 season=None, season_uuid=None, number=None, rating=None, aired=None, expiry=None):
        """
        :type uuid: str
        :type nodeid: str
        :type path: str
        :type channel: str
        :type program_title: str
        :type title: str
        :type description: str
        :type cover: str
        :type duration: int
        :type season: int
        :type season_uuid: str
        :type number: int
        :type rating: str
        :type aired: datetime
        :type expiry: datetime
        """
        self.uuid = uuid
        self.nodeid = nodeid
        self.path = path
        self.channel = channel
        self.program_title = program_title
        self.title = title
        self.description = description
        self.cover = cover
        self.duration = duration
        self.season = season
        self.season_uuid = season_uuid
        self.number = number
        self.rating = rating
        self.aired = aired
        self.expiry = expiry

    def __repr__(self):
        return "%r" % self.__dict__


class ContentApi:
    """ VIER/VIJF/ZES Content API"""
    API_ENDPOINT = 'https://api.viervijfzes.be'
    SITE_APIS = {
        'vier': 'https://www.vier.be/api',
        'vijf': 'https://www.vijf.be/api',
        'zes': 'https://www.zestv.be/api',
    }

    def __init__(self, auth=None):
        """ Initialise object """
        self._session = requests.session()
        self._auth = auth

    def get_programs(self, channel):
        """ Get a list of all programs of the specified channel.
        :type channel: str
        :rtype list[Program]
        NOTE: This function doesn't use an API.
        """
        if channel not in CHANNELS:
            raise Exception('Unknown channel %s' % channel)

        # Load webpage
        data = self._get_url(CHANNELS[channel]['url'])

        # Parse programs
        parser = HTMLParser()
        regex_programs = re.compile(r'<a class="program-overview__link" href="(?P<path>[^"]+)">\s+'
                                    r'<span class="program-overview__title">\s+(?P<title>[^<]+)</span>.*?'
                                    r'</a>', re.DOTALL)

        programs = []
        for item in regex_programs.finditer(data):
            path = item.group('path').lstrip('/')

            program = self.get_program(channel, path, CACHE_ONLY)  # Get program details, but from cache only
            if program:
                # Use program with metadata from cache
                programs.append(program)
            else:
                # Use program with the values that we've parsed from the page
                programs.append(Program(channel=channel,
                                        path=path,
                                        title=parser.unescape(item.group('title').strip())))
        return programs

    def get_program(self, channel, path, cache=CACHE_AUTO):
        """ Get a Program object from the specified page.
        :type channel: str
        :type path: str
        :type cache: int
        :rtype Program
        NOTE: This function doesn't use an API.
        """
        if channel not in CHANNELS:
            raise Exception('Unknown channel %s' % channel)

        if cache in [CACHE_AUTO, CACHE_ONLY]:
            # Try to fetch from cache
            data = kodiutils.get_cache(['program', channel, path])
            if data is None and cache == CACHE_ONLY:
                return None
        else:
            data = None

        if data is None:
            # Fetch webpage
            page = self._get_url(CHANNELS[channel]['url'] + '/' + path)

            # Extract JSON
            regex_program = re.compile(r'data-hero="([^"]+)', re.DOTALL)
            json_data = HTMLParser().unescape(regex_program.search(page).group(1))
            data = json.loads(json_data)['data']

            # Store response in cache
            kodiutils.set_cache(['program', channel, path], data)

        program = self._parse_program_data(data)

        return program

    def get_program_by_uuid(self, uuid, cache=CACHE_AUTO):
        """ Get a Program object.
        :type uuid: str
        :type cache: int
        :rtype Program
        """
        if cache in [CACHE_AUTO, CACHE_ONLY]:
            # Try to fetch from cache
            data = kodiutils.get_cache(['program', uuid])
            if data is None and cache == CACHE_ONLY:
                return None
        else:
            data = None

        if data is None:
            # Fetch from API
            response = self._get_url(self.API_ENDPOINT + '/content/%s' % uuid, authentication=True)
            data = json.loads(response)

            if not data:
                raise UnavailableException()

            # Store response in cache
            kodiutils.set_cache(['program', uuid], data)

        return Program(
            uuid=uuid,
            path=data['url']['S'].strip('/'),
            title=data['label']['S'],
            description=data['description']['S'],
            cover=data['image']['S'],
        )

    def get_episode(self, channel, path):
        """ Get a Episode object from the specified page.
        :type channel: str
        :type path: str
        :rtype Episode
        NOTE: This function doesn't use an API.
        """
        if channel not in CHANNELS:
            raise Exception('Unknown channel %s' % channel)

        # Load webpage
        page = self._get_url(CHANNELS[channel]['url'] + '/' + path)

        # Extract program JSON
        parser = HTMLParser()
        regex_program = re.compile(r'data-hero="([^"]+)', re.DOTALL)
        json_data = parser.unescape(regex_program.search(page).group(1))
        data = json.loads(json_data)['data']
        program = self._parse_program_data(data)

        # Extract episode JSON
        regex_episode = re.compile(r'<script type="application/json" data-drupal-selector="drupal-settings-json">(.*?)</script>', re.DOTALL)
        json_data = parser.unescape(regex_episode.search(page).group(1))
        data = json.loads(json_data)

        # Lookup the episode in the program JSON based on the nodeId
        # The episode we just found doesn't contain all information
        for episode in program.episodes:
            if episode.nodeid == data['pageInfo']['nodeId']:
                return episode

        return None

    def get_stream_by_uuid(self, uuid):
        """ Get the stream URL to use for this video.
        :type uuid: str
        :rtype str
        """
        response = self._get_url(self.API_ENDPOINT + '/content/%s' % uuid, authentication=True)
        data = json.loads(response)
        return data['video']['S']

    @staticmethod
    def _parse_program_data(data):
        """ Parse the Program JSON.
        :type data: dict
        :rtype Program
        """
        # Create Program info
        program = Program(
            uuid=data['id'],
            path=data['link'].lstrip('/'),
            channel=data['pageInfo']['site'],
            title=data['title'],
            description=data['description'],
            aired=datetime.fromtimestamp(data.get('pageInfo', {}).get('publishDate')),
            cover=data['images']['poster'],
            background=data['images']['hero'],
        )

        # Create Season info
        program.seasons = {
            key: Season(
                uuid=playlist['id'],
                path=playlist['link'].lstrip('/'),
                channel=playlist['pageInfo']['site'],
                title=playlist['title'],
                description=playlist['pageInfo']['description'],
                number=playlist['episodes'][0]['seasonNumber'],  # You did not see this
            )
            for key, playlist in enumerate(data['playlists'])
        }

        # Create Episodes info
        program.episodes = [
            ContentApi._parse_episode_data(episode, playlist['id'])
            for playlist in data['playlists']
            for episode in playlist['episodes']
        ]

        return program

    @staticmethod
    def _parse_episode_data(data, season_uuid):
        """ Parse the Episode JSON.
        :type data: dict
        :type season_uuid: str
        :rtype Episode
        """

        if data.get('episodeNumber'):
            episode_number = data.get('episodeNumber')
        else:
            # The episodeNumber can be absent
            match = re.compile(r'\d+$').search(data.get('title'))
            if match:
                episode_number = match.group(0)
            else:
                episode_number = None

        episode = Episode(
            uuid=data.get('videoUuid'),
            nodeid=data.get('pageInfo', {}).get('nodeId'),
            path=data.get('link').lstrip('/'),
            channel=data.get('pageInfo', {}).get('site'),
            program_title=data.get('program', {}).get('title'),
            title=data.get('title'),
            description=data.get('pageInfo', {}).get('description'),
            cover=data.get('image'),
            duration=data.get('duration'),
            season=data.get('seasonNumber'),
            season_uuid=season_uuid,
            number=episode_number,
            aired=datetime.fromtimestamp(data.get('createdDate')),
            expiry=datetime.fromtimestamp(data.get('unpublishDate')) if data.get('unpublishDate') else None,
            rating=data.get('parentalRating')
        )
        return episode

    def _get_url(self, url, params=None, authentication=False):
        """ Makes a GET request for the specified URL.
        :type url: str
        :rtype str
        """
        if authentication:
            if not self._auth:
                raise Exception('Requested to authenticate, but not auth object passed')
            response = self._session.get(url, params=params, headers={
                'authorization': self._auth.get_token(),
            })
        else:
            response = self._session.get(url, params=params)

        if response.status_code != 200:
            _LOGGER.error(response.text)
            raise Exception('Could not fetch data')

        return response.text
