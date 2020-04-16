# -*- coding: utf-8 -*-
""" AUTH API """

from __future__ import absolute_import, division, unicode_literals

import json
import logging
import os
import re
import time
from datetime import datetime

from six.moves.html_parser import HTMLParser
import requests

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

    def __init__(self, uuid=None, path=None, channel=None, title=None, description=None, aired=None, cover=None, background=None, seasons=None, episodes=None, clips=None):
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
        :type clips: list[Clip]
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
        self.clips = clips

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

class Clip:
    """ Defines a Clip. """

    def __init__(self, uuid=None, path=None, channel=None, program_title=None, title=None, description=None, cover=None, duration=None):
        """
        :type uuid: str
        :type path: str
        :type channel: str
        :type program_title: str
        :type title: str
        :type description: str
        :type cover: str
        :type duration: int
        """
        self.uuid = uuid
        self.path = path
        self.channel = channel
        self.program_title = program_title
        self.title = title
        self.description = description
        self.cover = cover
        self.duration = duration

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

    def __init__(self, auth=None, cache_path=None):
        """ Initialise object """
        self._session = requests.session()
        self._auth = auth
        self._cache_path = cache_path

    def get_programs(self, channel, cache=CACHE_AUTO):
        """ Get a list of all programs of the specified channel.
        :type channel: str
        :type cache: str
        :rtype list[Program]
        """
        if channel not in CHANNELS:
            raise Exception('Unknown channel %s' % channel)

        def update():
            """ Fetch the program listing by scraping """
            # Load webpage
            raw_html = self._get_url(CHANNELS[channel]['url'])

            # Parse programs
            parser = HTMLParser()
            regex_programs = re.compile(r'<a class="program-overview__link" href="(?P<path>[^"]+)">\s+'
                                        r'<span class="program-overview__title">\s+(?P<title>[^<]+)</span>.*?'
                                        r'</a>', re.DOTALL)
            data = {
                item.group('path').lstrip('/'): parser.unescape(item.group('title').strip())
                for item in regex_programs.finditer(raw_html)
            }

            if not data:
                raise Exception('No programs found for %s' % channel)

            return data

        # Fetch listing from cache or update if needed
        data = self._handle_cache(key=['programs', channel], cache_mode=cache, update=update, ttl=30 * 5)
        if not data:
            return []

        programs = []
        for path in data:
            title = data[path]
            program = self.get_program(channel, path, CACHE_ONLY)  # Get program details, but from cache only
            if program:
                # Use program with metadata from cache
                programs.append(program)
            else:
                # Use program with the values that we've parsed from the page
                programs.append(Program(channel=channel,
                                        path=path,
                                        title=title))
        return programs

    def get_program(self, channel, path, cache=CACHE_AUTO):
        """ Get a Program object from the specified page.
        :type channel: str
        :type path: str
        :type cache: int
        :rtype Program
        """
        if channel not in CHANNELS:
            raise Exception('Unknown channel %s' % channel)

        def update():
            """ Fetch the program metadata by scraping """
            # Fetch webpage
            page = self._get_url(CHANNELS[channel]['url'] + '/' + path)

            # Extract JSON
            regex_program = re.compile(r'data-hero="([^"]+)', re.DOTALL)
            json_data = HTMLParser().unescape(regex_program.search(page).group(1))
            data = json.loads(json_data)['data']

            # Extract clips
            parser = HTMLParser()
            regex_clips = re.compile(r'<a class="teaser card-teaser ui-animated has-duration-bar" href="(?P<path>[^"]+)[\s\S]*?'
                                     r'data-background-image="(?P<cover>[^"]+)[\s\S]*?'
                                     r'data-duration="(?P<duration>[^"]+)[\s\S]*?'
                                     r'data-videoid="(?P<uuid>[^"]+)[\s\S]*?'
                                     r'card-teaser__title"><span>(?P<title>[^.*]+)</span>[\s\S]*?'
                                     r'</a>', re.DOTALL)

            clips = [
                [item.group('path'), item.group('cover'), str(item.group('duration')), item.group('uuid'), parser.unescape(item.group('title')), channel]
                for item in regex_clips.finditer(page)
            ]

            _LOGGER.warning(str('aantal: ' + str(len(clips))))
            _LOGGER.warning(str('elementen: ' + str(len(clips[0]))))

            
            return [data, clips]

        # Fetch listing from cache or update if needed
        data, clips = self._handle_cache(key=['program', channel, path], cache_mode=cache, update=update)
        program = self._parse_program_data(data, clips)

        return program

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
        program = self._parse_program_data(data, None)

        # Extract episode JSON
        regex_episode = re.compile(r'<script type="application/json" data-drupal-selector="drupal-settings-json">(.*?)</script>', re.DOTALL)
        json_data = parser.unescape(regex_episode.search(page).group(1))
        data = json.loads(json_data)

        # Extract clips data


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
    def _parse_program_data(data, clips):
        """ Parse the Program JSON.
        :type data: dict
        :type clips: list
        :rtype Program
        """
        if data is None:
            return None

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
            for key, playlist in enumerate(data['playlists']) if playlist['episodes']
        }

        # Create Episodes info
        program.episodes = [
            ContentApi._parse_episode_data(episode, playlist['id'])
            for playlist in data['playlists']
            for episode in playlist['episodes']
        ]

        program.clips = [
            Clip(
                uuid=clip[3],
                path=clip[0],
                channel=clip[5],
                program_title='title',
                title=clip[4],
                description='',
                cover=clip[1],
                duration=clip[2]
            )
            for clip in clips
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

    def _handle_cache(self, key, cache_mode, update, ttl=30 * 24 * 60 * 60):
        """ Fetch something from the cache, and update if needed """
        data = [None, None]
        if cache_mode in [CACHE_AUTO, CACHE_ONLY]:
            # Try to fetch from cache
            data[0] = self._get_cache(key)
            if data[0] is None and cache_mode == CACHE_ONLY:
                return [None, None]
        else:
            data[0] = None

        if data[0] is None:
            #try:
                # Fetch fresh data
            _LOGGER.debug('Fetching fresh data for key %s', '.'.join(key))
            data = update()
            _LOGGER.warning(data)
            if data:
                # Store fresh response in cache
                self._set_cache(key, data[0], ttl)
#            except Exception as exc:  # pylint: disable=broad-except
#                _LOGGER.warning('Something went wrong when refreshing live data: %s. Using expired cached values.', exc)
#                data[0] = self._get_cache(key, allow_expired=True)
#                data[1] = None

        return data

    def _get_cache(self, key, allow_expired=False):
        """ Get an item from the cache """
        filename = '.'.join(key) + '.json'
        fullpath = self._cache_path + filename

        if not os.path.exists(fullpath):
            return None

        if not allow_expired and os.stat(fullpath).st_mtime < time.time():
            return None

        with open(fullpath, 'r') as fdesc:
            try:
                _LOGGER.debug('Fetching %s from cache', filename)
                value = json.load(fdesc)
                return value
            except (ValueError, TypeError):
                return None

    def _set_cache(self, key, data, ttl):
        """ Store an item in the cache """
        filename = '.'.join(key) + '.json'
        fullpath = self._cache_path + filename

        if not os.path.exists(self._cache_path):
            os.mkdir(self._cache_path)

        with open(fullpath, 'w') as fdesc:
            _LOGGER.debug('Storing to cache as %s', filename)
            json.dump(data, fdesc)

        # Set TTL by modifying modification date
        deadline = int(time.time()) + ttl
        os.utime(fullpath, (deadline, deadline))
