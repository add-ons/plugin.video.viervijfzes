# -*- coding: utf-8 -*-
""" Player module """

from __future__ import absolute_import, division, unicode_literals

import logging
import os

from resources.lib import kodiutils
from resources.lib.downloader import Downloader
from resources.lib.viervijfzes.auth import AuthApi
from resources.lib.viervijfzes.auth_awsidp import InvalidLoginException, AuthenticationException
from resources.lib.viervijfzes.content import ContentApi, UnavailableException, GeoblockedException

_LOGGER = logging.getLogger('player')


class Player:
    """ Code responsible for playing media """

    def __init__(self):
        """ Initialise object """
        auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())
        self._api = ContentApi(auth)

    def play_from_page(self, channel, path):
        """ Play the requested item.
        :type channel: string
        :type path: string
        """
        # Get episode information
        episode = ContentApi().get_episode(channel, path)

        # Play this now we have the uuid
        self.play(episode.uuid)

    def play(self, uuid):
        """ Play the requested item.
        :type uuid: string
        """
        if kodiutils.get_setting_bool('episode_cache_enabled'):
            # Check for a cached version
            cached_file = self._check_cached_episode(uuid)
            if cached_file:
                kodiutils.play(cached_file)
                return

        # Workaround for Raspberry Pi 3 and older
        omxplayer = kodiutils.get_global_setting('videoplayer.useomxplayer')
        if omxplayer is False:
            kodiutils.set_global_setting('videoplayer.useomxplayer', True)

        # Resolve the stream
        resolved_stream = self._fetch_stream(uuid)
        if not resolved_stream:
            kodiutils.end_of_directory()
            return

        # Play this item
        kodiutils.play(resolved_stream)

    def download(self, uuid):
        """ Download the requested item to cache.
        :type uuid: string
        """
        # We can notify Kodi already that we won't be returning a listing.
        # This also fixes an odd Kodi bug where a starting a Progress() without closing the directory listing causes Kodi to hang.
        kodiutils.end_of_directory()

        # Check ffmpeg
        if not Downloader.check():
            kodiutils.ok_dialog(message=kodiutils.localize(30719))  # Could not download this episode since ffmpeg seems to be unavailable.
            return

        # Check download folder
        download_folder = kodiutils.get_setting('episode_cache_folder').rstrip('/')
        if not os.path.exists(download_folder):
            kodiutils.ok_dialog(message=kodiutils.localize(30718))  # Could not download this episode since the download folder is not set or does not exist.
            return

        # Check if we already have downloaded this file
        download_path = '%s/%s.mp4' % (download_folder, uuid)
        if os.path.isfile(download_path):
            # You have already downloaded this episode. Do you want to download it again?
            result = kodiutils.yesno_dialog(message=kodiutils.localize(30726))
            if not result:
                return

        # Download this item
        downloader = Downloader()
        progress = kodiutils.progress(message=kodiutils.localize(30723))  # Starting download...

        def callback(total, current):
            """ Callback function to update the progress bar. """
            percentage = current * 100 / total
            progress.update(int(percentage), kodiutils.localize(30724, amount=round(percentage, 2)))  # Downloading... ({amount}%)
            return progress.iscanceled()

        # Resolve the stream and start the download
        resolved_stream = self._fetch_stream(uuid)
        status = downloader.download(resolved_stream, download_path, callback)

        # Close the progress bar
        progress.close()

        if status:
            kodiutils.ok_dialog(message=kodiutils.localize(30725))  # Download has finished. You can now play this episode from cache.

    def _fetch_stream(self, uuid):
        """ Fetches the HLS stream of the item.
        :type uuid: string
        """
        try:
            # Check if we have credentials
            if not kodiutils.get_setting('username') or not kodiutils.get_setting('password'):
                confirm = kodiutils.yesno_dialog(
                    message=kodiutils.localize(30701))  # To watch a video, you need to enter your credentials. Do you want to enter them now?
                if confirm:
                    kodiutils.open_settings()
                return None

            try:
                # Get stream information
                resolved_stream = self._api.get_stream_by_uuid(uuid)

            except (InvalidLoginException, AuthenticationException) as ex:
                _LOGGER.error(ex)
                kodiutils.ok_dialog(message=kodiutils.localize(30702, error=str(ex)))
                return None

        except GeoblockedException:
            kodiutils.ok_dialog(heading=kodiutils.localize(30709), message=kodiutils.localize(30710))  # This video is geo-blocked...
            return None

        except UnavailableException:
            kodiutils.ok_dialog(heading=kodiutils.localize(30711), message=kodiutils.localize(30712))  # The video is unavailable...
            return None

        return resolved_stream

    @staticmethod
    def _check_cached_episode(uuid):
        """ Check if this episode is available in the download cache.
        :type uuid: string
        """
        download_folder = kodiutils.get_setting('episode_cache_folder').rstrip('/')
        if not download_folder or not os.path.exists(download_folder):
            return None

        # Check if we already have downloaded this file
        download_path = '%s/%s.mp4' % (download_folder, uuid)
        if os.path.isfile(download_path):
            # You have cached this episode. Do you want to play from your cache or stream it?
            result = kodiutils.yesno_dialog(message=kodiutils.localize(30720),
                                            yeslabel=kodiutils.localize(30721),  # Stream
                                            nolabel=kodiutils.localize(30722))  # Play from cache

            if not result:
                return download_path

        return None
