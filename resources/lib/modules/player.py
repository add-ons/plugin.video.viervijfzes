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

    def play_from_page(self, channel, path):
        """ Play the requested item.
        :type channel: string
        :type path: string
        """
        # Get episode information
        episode = ContentApi().get_episode(channel, path)

        # Play this now we have the uuid
        self.play(channel, episode.uuid)

    @staticmethod
    def play(channel, item):
        """ Play the requested item.
        :type channel: string
        :type item: string
        """
        try:
            # Check if we have credentials
            if not kodiutils.get_setting('username') or not kodiutils.get_setting('password'):
                confirm = kodiutils.yesno_dialog(message=kodiutils.localize(30701))  # To watch a video, you need to enter your credentials. Do you want to enter them now?
                if confirm:
                    kodiutils.open_settings()
                kodiutils.end_of_directory()
                return

            # Fetch an auth token now
            auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())
            token = auth.get_token()

            # Get stream information
            resolved_stream = ContentApi(token).get_stream(channel, item)

        except GeoblockedException:
            kodiutils.ok_dialog(heading=kodiutils.localize(30709), message=kodiutils.localize(30710))  # This video is geo-blocked...
            return

        except UnavailableException:
            kodiutils.ok_dialog(heading=kodiutils.localize(30711), message=kodiutils.localize(30712))  # The video is unavailable...
            return

        # Play this item
        kodiutils.play(resolved_stream)
