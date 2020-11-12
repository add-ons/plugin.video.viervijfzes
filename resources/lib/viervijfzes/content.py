# -*- coding: utf-8 -*-
""" AUTH API """

from __future__ import absolute_import, division, unicode_literals

import json
import logging
import os
import re
import time
from datetime import datetime

import requests
from six.moves.html_parser import HTMLParser  # pylint: disable=wrong-import-order

from resources.lib.kodiutils import STREAM_DASH, STREAM_HLS
from resources.lib.viervijfzes import CHANNELS, ResolvedStream

_LOGGER = logging.getLogger(__name__)

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

    def __init__(self, uuid=None, path=None, channel=None, title=None, description=None, aired=None, cover=None, background=None, seasons=None, episodes=None,
                 clips=None):
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
        :type clips: list[Episode]
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

    def __init__(self, uuid=None, video_type=None, nodeid=None, path=None, channel=None, program_title=None, title=None, description=None, cover=None,
                 background=None, duration=None, season=None, season_uuid=None, number=None, rating=None, aired=None, expiry=None, stream=None):
        """
        :type uuid: str
        :type video_type: str
        :type nodeid: str
        :type path: str
        :type channel: str
        :type program_title: str
        :type title: str
        :type description: str
        :type cover: str
        :type background: str
        :type duration: int
        :type season: int
        :type season_uuid: str
        :type number: int
        :type rating: str
        :type aired: datetime
        :type expiry: datetime
        :type stream: string
        """
        self.uuid = uuid
        self.video_type = video_type
        self.nodeid = nodeid
        self.path = path
        self.channel = channel
        self.program_title = program_title
        self.title = title
        self.description = description
        self.cover = cover
        self.background = background
        self.duration = duration
        self.season = season
        self.season_uuid = season_uuid
        self.number = number
        self.rating = rating
        self.aired = aired
        self.expiry = expiry
        self.stream = stream

    def __repr__(self):
        return "%r" % self.__dict__


class Category:
    """ Defines a Category. """

    def __init__(self, uuid=None, channel=None, title=None, programs=None, episodes=None):
        """
        :type uuid: str
        :type channel: str
        :type title: str
        :type programs: List[Program]
        :type episodes: List[Episode]
        """
        self.uuid = uuid
        self.channel = channel
        self.title = title
        self.programs = programs
        self.episodes = episodes

    def __repr__(self):
        return "%r" % self.__dict__


class ContentApi:
    """ VIER/VIJF/ZES Content API"""
    API_ENDPOINT = 'https://api.viervijfzes.be'
    API2_ENDPOINT = 'https://api2.viervijfzes.be'
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
            program = self.get_program(channel, path, cache=CACHE_ONLY)  # Get program details, but from cache only
            if program:
                # Use program with metadata from cache
                programs.append(program)
            else:
                # Use program with the values that we've parsed from the page
                programs.append(Program(channel=channel,
                                        path=path,
                                        title=title))
        return programs

    def get_program(self, channel, path, extract_clips=False, cache=CACHE_AUTO):
        """ Get a Program object from the specified page.
        :type channel: str
        :type path: str
        :type extract_clips: bool
        :type cache: int
        :rtype Program
        """
        if channel not in CHANNELS:
            raise Exception('Unknown channel %s' % channel)

        # We want to use the html to extract clips
        # This is the worst hack, since Python 2.7 doesn't support nonlocal
        raw_html = [None]

        def update():
            """ Fetch the program metadata by scraping """
            # Fetch webpage
            page = self._get_url(CHANNELS[channel]['url'] + '/' + path)

            # Store a copy in the parent's raw_html var.
            raw_html[0] = page

            # Extract JSON
            regex_program = re.compile(r'data-hero="([^"]+)', re.DOTALL)
            json_data = HTMLParser().unescape(regex_program.search(page).group(1))
            data = json.loads(json_data)['data']

            return data

        # Fetch listing from cache or update if needed
        data = self._handle_cache(key=['program', channel, path], cache_mode=cache, update=update)
        if not data:
            return None

        program = self._parse_program_data(data)

        # Also extract clips if we did a real HTTP call
        if extract_clips and raw_html[0]:
            clips = self._extract_videos(raw_html[0], channel)
            program.clips = clips

        return program

    def get_episode(self, channel, path, cache=CACHE_AUTO):
        """ Get a Episode object from the specified page.
        :type channel: str
        :type path: str
        :type cache: str
        :rtype Episode
        """
        if channel not in CHANNELS:
            raise Exception('Unknown channel %s' % channel)

        def update():
            """ Fetch the program metadata by scraping """
            # Load webpage
            page = self._get_url(CHANNELS[channel]['url'] + '/' + path)

            parser = HTMLParser()
            program_json = None
            episode_json = None

            # Extract video JSON by looking for a data-video tag
            # This is not present on every page
            regex_video_data = re.compile(r'data-video="([^"]+)"', re.DOTALL)
            result = regex_video_data.search(page)
            if result:
                video_id = json.loads(parser.unescape(result.group(1)))['id']
                video_json_data = self._get_url('%s/video/%s' % (self.SITE_APIS[channel], video_id))
                video_json = json.loads(video_json_data)
                return dict(video=video_json)

            # Extract program JSON
            regex_program = re.compile(r'data-hero="([^"]+)', re.DOTALL)
            result = regex_program.search(page)
            if result:
                program_json_data = parser.unescape(result.group(1))
                program_json = json.loads(program_json_data)['data']

            # Extract episode JSON
            regex_episode = re.compile(r'<script type="application/json" data-drupal-selector="drupal-settings-json">(.*?)</script>', re.DOTALL)
            result = regex_episode.search(page)
            if result:
                episode_json_data = parser.unescape(result.group(1))
                episode_json = json.loads(episode_json_data)

            return dict(program=program_json, episode=episode_json)

        # Fetch listing from cache or update if needed
        data = self._handle_cache(key=['episode', channel, path], cache_mode=cache, update=update)
        if not data:
            return None

        if 'video' in data and data['video']:
            # We have found detailed episode information
            episode = self._parse_episode_data(data['video'])
            return episode

        if 'program' in data and 'episode' in data and data['program'] and data['episode']:
            # We don't have detailed episode information
            # We need to lookup the episode in the program JSON
            program = self._parse_program_data(data['program'])
            for episode in program.episodes:
                if episode.nodeid == data['episode']['pageInfo']['nodeId']:
                    return episode

        return None

    def get_stream_by_uuid(self, uuid):
        """ Get the stream URL to use for this video.
        :type uuid: str
        :rtype str
        """
        response = self._get_url(self.API_ENDPOINT + '/content/%s' % uuid, authentication=True)
        data = json.loads(response)

        if 'videoDash' in data:
            # DRM protected stream
            # See https://docs.unified-streaming.com/documentation/drm/buydrm.html#setting-up-the-client
            drm_key = data['drmKey']['S']

            _LOGGER.debug('Fetching Authentication XML with drm_key %s', drm_key)
            response_drm = self._get_url(self.API2_ENDPOINT + '/decode/%s' % drm_key, authentication=True)
            data_drm = json.loads(response_drm)

            return ResolvedStream(
                uuid=uuid,
                url=data['videoDash']['S'],
                stream_type=STREAM_DASH,
                license_url='https://wv-keyos.licensekeyserver.com/',
                auth=data_drm.get('auth'),
            )

        # Normal HLS stream
        return ResolvedStream(
            uuid=uuid,
            url=data['video']['S'],
            stream_type=STREAM_HLS,
        )

    def get_categories(self, channel):
        """ Get a list of all categories of the specified channel.
        :type channel: str
        :rtype list[Category]
        """
        if channel not in CHANNELS:
            raise Exception('Unknown channel %s' % channel)

        # Load webpage
        raw_html = self._get_url(CHANNELS[channel]['url'])

        # Categories regexes
        regex_articles = re.compile(r'<article([^>]+)>(.*?)</article>', re.DOTALL)
        regex_submenu_id = re.compile(r'data-submenu-id="([^"]*)"')  # splitted since the order might change
        regex_submenu_title = re.compile(r'data-submenu-title="([^"]*)"')

        categories = []
        for result in regex_articles.finditer(raw_html):
            article_info_html = result.group(1)
            article_html = result.group(2)
            category_title = regex_submenu_title.search(article_info_html).group(1)
            category_id = regex_submenu_id.search(article_info_html).group(1)

            # Skip empty categories or 'All programs'
            if not category_id or category_id == 'programmas':
                continue

            # Extract items
            programs = self._extract_programs(article_html, channel)
            episodes = self._extract_videos(article_html, channel)
            categories.append(Category(uuid=category_id, channel=channel, title=category_title, programs=programs, episodes=episodes))

        return categories

    def get_weather(self, channel):
        """ Get a weather dictionary.
        :type channel: str
        :rtype dict
        """
        response = self._get_url(self.SITE_APIS[channel] + '/weather', authentication=True)
        weather = json.loads(response)
        return weather

    def get_ad_streams(self, channel, program, path, uuid, video_type, username):
        """ Get a list of advertisement stream URLs to use for this video.
        :type channel: str
        :type path: str
        :rtype list
        """
        ad_streams = []
        ad_url = 'https://pubads.g.doubleclick.net/gampad/ads'
        weather = self.get_weather(channel)
        channel_info = dict(
            vier=dict(cmsid='2493239', network_id='21797861328'),
            vijf=dict(cmsid='2493512', network_id='21797861328'),
            zes=dict(cmsid='2496240', network_id='21797861328')
        )
        network_id = channel_info.get(channel).get('network_id')
        from unicodedata import normalize
        program = normalize('NFD', program).replace(' ', '-')
        program = re.sub(r'[^A-Za-z0-9-]+', '', program).lower()
        from hashlib import sha1
        ppid = sha1(username.encode('utf-8')).hexdigest()
        if program:
            iu_id = '/{}/{}/{}/{}'.format(network_id, channel, 'programmas', program)
        else:
            iu_id = '/{}/{}/'.format(network_id, channel)
        params = dict(ad_rule=1,
                      cmsid=channel_info.get(channel).get('cmsid'),
                      correlator=int(round(time.time() * 1000)),
                      sbs_weather_cond=weather.get('summary'),
                      sbs_weather_temp=weather.get('temperature'),
                      description_url=path,
                      env='vp',
                      gdfp_req=1,
                      impl='s',
                      iu=iu_id,
                      output='vast',
                      pp='SBSNoDash',
                      ppid=ppid,
                      sz='640x360',
                      unviewed_position_start=1,
                      url=path,
                      vid=uuid,
                      video_type=video_type)

        xml = self._get_url(ad_url, params)
        import xml.etree.ElementTree as ET
        tree = ET.fromstring(xml)
        for item in tree:
            if item.tag == 'Preroll':
                url = item.find('Ad').text
                xml = self._get_url(url)
                tree = ET.fromstring(xml)
                for adv in tree.findall('.//Ad'):
                    for stream in adv.findall('.//MediaFile'):
                        if stream.get('type') == 'video/mp4' and stream.get('width') == '1920':
                            ad_streams.append(stream.text)
                            break
        return ad_streams

    @staticmethod
    def _extract_programs(html, channel):
        """ Extract Programs from HTML code """
        parser = HTMLParser()

        # Item regexes
        regex_item = re.compile(r'<a[^>]+?href="(?P<path>[^"]+)"[^>]+?>'
                                r'.*?<h3 class="poster-teaser__title"><span>(?P<title>[^<]*)</span></h3>.*?'
                                r'</a>', re.DOTALL)

        # Extract items
        programs = []
        for item in regex_item.finditer(html):
            path = item.group('path')
            if path.startswith('/video'):
                continue

            title = parser.unescape(item.group('title'))

            # Program
            programs.append(Program(
                path=path.lstrip('/'),
                channel=channel,
                title=title,
            ))

        return programs

    @staticmethod
    def _extract_videos(html, channel):
        """ Extract videos from HTML code """
        parser = HTMLParser()

        # Item regexes
        regex_item = re.compile(r'<a[^>]+?href="(?P<path>[^"]+)"[^>]+?>.*?</a>', re.DOTALL)

        # Episode regexes
        regex_episode_title = re.compile(r'<h3 class="(?:poster|card|image)-teaser__title">(?:<span>)?([^<]*)(?:</span>)?</h3>')
        regex_episode_program = re.compile(r'<div class="card-teaser__label">([^<]*)</div>')
        regex_episode_duration = re.compile(r'data-duration="([^"]*)"')
        regex_episode_video_id = re.compile(r'data-videoid="([^"]*)"')
        regex_episode_image = re.compile(r'data-background-image="([^"]*)"')
        regex_episode_timestamp = re.compile(r'data-timestamp="([^"]*)"')

        # Extract items
        episodes = []
        for item in regex_item.finditer(html):
            item_html = item.group(0)
            path = item.group('path')

            # Extract title
            try:
                title = parser.unescape(regex_episode_title.search(item_html).group(1))
            except AttributeError:
                continue

            # This is not a episode
            if not path.startswith('/video'):
                continue

            try:
                episode_program = regex_episode_program.search(item_html).group(1)
            except AttributeError:
                _LOGGER.warning('Found no episode_program for %s', title)
                episode_program = None
            try:
                episode_duration = int(regex_episode_duration.search(item_html).group(1))
            except AttributeError:
                _LOGGER.warning('Found no episode_duration for %s', title)
                episode_duration = None
            try:
                episode_video_id = regex_episode_video_id.search(item_html).group(1)
            except AttributeError:
                _LOGGER.warning('Found no episode_video_id for %s', title)
                episode_video_id = None
            try:
                episode_image = parser.unescape(regex_episode_image.search(item_html).group(1))
            except AttributeError:
                _LOGGER.warning('Found no episode_image for %s', title)
                episode_image = None
            try:
                episode_timestamp = int(regex_episode_timestamp.search(item_html).group(1))
            except AttributeError:
                _LOGGER.warning('Found no episode_timestamp for %s', title)
                episode_timestamp = None

            # Episode
            episodes.append(Episode(
                path=path.lstrip('/'),
                channel=channel,
                title=title,
                duration=episode_duration,
                uuid=episode_video_id,
                aired=datetime.fromtimestamp(episode_timestamp) if episode_timestamp else None,
                cover=episode_image,
                program_title=episode_program,
            ))

        return episodes

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
            for key, playlist in enumerate(data['playlists']) if playlist['episodes']
        }

        # Create Episodes info
        program.episodes = [
            ContentApi._parse_episode_data(episode, playlist['id'])
            for playlist in data['playlists']
            for episode in playlist['episodes']
        ]

        return program

    @staticmethod
    def _parse_episode_data(data, season_uuid=None):
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
            video_type=data.get('type', {}),
            nodeid=data.get('pageInfo', {}).get('nodeId'),
            path=data.get('link').lstrip('/'),
            channel=data.get('pageInfo', {}).get('site'),
            program_title=data.get('program', {}).get('title') if data.get('program') else data.get('title'),
            title=data.get('title'),
            description=data.get('pageInfo', {}).get('description'),
            cover=data.get('image'),
            background=data.get('image'),
            duration=data.get('duration'),
            season=data.get('seasonNumber'),
            season_uuid=season_uuid,
            number=episode_number,
            aired=datetime.fromtimestamp(data.get('createdDate')),
            expiry=datetime.fromtimestamp(data.get('unpublishDate')) if data.get('unpublishDate') else None,
            rating=data.get('parentalRating'),
            stream=data.get('path'),
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
        if cache_mode in [CACHE_AUTO, CACHE_ONLY]:
            # Try to fetch from cache
            data = self._get_cache(key)
            if data is None and cache_mode == CACHE_ONLY:
                return None
        else:
            data = None

        if data is None:
            try:
                # Fetch fresh data
                _LOGGER.debug('Fetching fresh data for key %s', '.'.join(key))
                data = update()
                if data:
                    # Store fresh response in cache
                    self._set_cache(key, data, ttl)
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.warning('Something went wrong when refreshing live data: %s. Using expired cached values.', exc)
                data = self._get_cache(key, allow_expired=True)

        return data

    def _get_cache(self, key, allow_expired=False):
        """ Get an item from the cache """
        filename = ('.'.join(key) + '.json').replace('/', '_')
        fullpath = os.path.join(self._cache_path, filename)

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
        filename = ('.'.join(key) + '.json').replace('/', '_')
        fullpath = os.path.join(self._cache_path, filename)

        if not os.path.exists(self._cache_path):
            os.makedirs(self._cache_path)

        with open(fullpath, 'w') as fdesc:
            _LOGGER.debug('Storing to cache as %s', filename)
            json.dump(data, fdesc)

        # Set TTL by modifying modification date
        deadline = int(time.time()) + ttl
        os.utime(fullpath, (deadline, deadline))
