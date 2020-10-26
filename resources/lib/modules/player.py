# -*- coding: utf-8 -*-
""" Player module """

from __future__ import absolute_import, division, unicode_literals

import logging

from resources.lib import kodiutils
from resources.lib.modules.menu import Menu
from resources.lib.viervijfzes import CHANNELS
from resources.lib.viervijfzes.auth import AuthApi
from resources.lib.viervijfzes.auth_awsidp import AuthenticationException, InvalidLoginException
from resources.lib.viervijfzes.content import ContentApi, GeoblockedException, UnavailableException

_LOGGER = logging.getLogger(__name__)


class Player:
    """ Code responsible for playing media """

    def __init__(self):
        """ Initialise object """
        auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())
        self._api = ContentApi(auth, cache_path=kodiutils.get_cache_path())

        # Workaround for Raspberry Pi 3 and older
        kodiutils.set_global_setting('videoplayer.useomxplayer', True)

    @staticmethod
    def live(channel):
        """ Play the live channel.
        :type channel: string
        """
        channel_name = CHANNELS.get(channel, dict(name=channel))
        kodiutils.ok_dialog(message=kodiutils.localize(30718, channel=channel_name.get('name')))  # There is no live stream available for {channel}.
        kodiutils.end_of_directory()

    def play_from_page(self, channel, path):
        """ Play the requested item.
        :type channel: string
        :type path: string
        """
        # Get episode information
        episode = self._api.get_episode(channel, path)
        resolved_stream = None

        if episode is None:
            kodiutils.ok_dialog(message=kodiutils.localize(30712))
            return

        if episode.stream:
            # We already have a resolved stream. Nice!
            # We don't need credentials for these streams.
            resolved_stream = episode.stream
            _LOGGER.debug('Already got a resolved stream: %s', resolved_stream)

        if episode.uuid:
            # Lookup the stream
            resolved_stream = self._resolve_stream(episode.uuid)
            _LOGGER.debug('Resolved stream: %s', resolved_stream)

        if resolved_stream:
            titleitem = Menu.generate_titleitem(episode)
            kodiutils.play(resolved_stream, info_dict=titleitem.info_dict, art_dict=titleitem.art_dict, prop_dict=titleitem.prop_dict)

    def play(self, uuid):
        """ Play the requested item.
        :type uuid: string
        """
        # Lookup the stream
        resolved_stream = self._resolve_stream(uuid)
        kodiutils.play(resolved_stream)

    @staticmethod
    def _resolve_stream(uuid):
        """ Resolve the stream for the requested item
        :type uuid: string
        """
        try:
            # Check if we have credentials
            if not kodiutils.get_setting('username') or not kodiutils.get_setting('password'):
                confirm = kodiutils.yesno_dialog(
                    message=kodiutils.localize(30701))  # To watch a video, you need to enter your credentials. Do you want to enter them now?
                if confirm:
                    kodiutils.open_settings()
                kodiutils.end_of_directory()
                return None

            # Fetch an auth token now
            try:
                auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())

                # Get stream information
                resolved_stream = ContentApi(auth).get_stream_by_uuid(uuid)
                return resolved_stream

            except (InvalidLoginException, AuthenticationException) as ex:
                _LOGGER.error(ex)
                kodiutils.ok_dialog(message=kodiutils.localize(30702, error=str(ex)))
                kodiutils.end_of_directory()
                return None

        except GeoblockedException:
            kodiutils.ok_dialog(heading=kodiutils.localize(30709), message=kodiutils.localize(30710))  # This video is geo-blocked...
            return None

        except UnavailableException:
            kodiutils.ok_dialog(heading=kodiutils.localize(30711), message=kodiutils.localize(30712))  # The video is unavailable...
            return None
