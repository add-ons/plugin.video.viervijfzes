# -*- coding: utf-8 -*-
""" Player module """

from __future__ import absolute_import, division, unicode_literals

import logging

from resources.lib import kodiutils
from resources.lib.viervijfzes.auth import AuthApi
from resources.lib.viervijfzes.content import ContentApi, UnavailableException, GeoblockedException

_LOGGER = logging.getLogger('player')


class Player:
    """ Code responsible for playing media """

    def __init__(self):
        """ Initialise object """
        self._auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())
        self._api = ContentApi(self._auth.get_token())

    def play_from_page(self, channel, path):
        """ Play the requested item.
        :type channel: string
        :type path: string
        """
        # Get episode information
        episode = self._api.get_episode(channel, path)

        # Play this now we have the uuid
        self.play(channel, episode.uuid)

    def play(self, channel, item):
        """ Play the requested item.
        :type channel: string
        :type item: string
        """
        try:
            # Get stream information
            resolved_stream = self._api.get_stream(channel, item)

        except GeoblockedException:
            kodiutils.ok_dialog(heading=kodiutils.localize(30709), message=kodiutils.localize(30710))  # This video is geo-blocked...
            return

        except UnavailableException:
            kodiutils.ok_dialog(heading=kodiutils.localize(30711), message=kodiutils.localize(30712))  # The video is unavailable...
            return

        # Play this item
        kodiutils.play(resolved_stream)
