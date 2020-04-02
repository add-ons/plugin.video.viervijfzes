# -*- coding: utf-8 -*-
""" Tests for the episode downloader """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

from resources.lib import kodiutils
from resources.lib.downloader import Downloader
from resources.lib.viervijfzes.auth import AuthApi
from resources.lib.viervijfzes.content import ContentApi, Program

_LOGGER = logging.getLogger('test-downloader')


class TestDownloader(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestDownloader, self).__init__(*args, **kwargs)
        auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())
        self._api = ContentApi(auth, cache_path=kodiutils.get_cache_path())

    def test_check(self):
        """ Test if ffmpeg is installed. """
        status = Downloader.check()
        self.assertTrue(status)

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_download(self):
        """ Test to download a stream. """
        program = self._api.get_program('vier', 'de-mol')
        self.assertIsInstance(program, Program)

        episode = program.episodes[0]
        stream = self._api.get_stream_by_uuid(episode.uuid)
        filename = '/tmp/download-test.mp4'

        def progress_callback(total, seconds):
            _LOGGER.info('Downloading... Progress = %d / %d seconds', seconds, total)

            # Terminate when we have downloaded 5 seconds, we just want to test this
            return seconds > 5

        status = Downloader().download(stream=stream, output=filename, progress_callback=progress_callback)
        self.assertFalse(status)  # status is false since we cancelled


if __name__ == '__main__':
    unittest.main()
