# -*- coding: utf-8 -*-
""" Tests for Content API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

import resources.lib.kodiutils as kodiutils
from resources.lib.viervijfzes import ResolvedStream
from resources.lib.viervijfzes.auth import AuthApi
from resources.lib.viervijfzes.content import ContentApi, Program, Episode, CACHE_PREVENT

_LOGGER = logging.getLogger(__name__)


class TestApi(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestApi, self).__init__(*args, **kwargs)
        auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())
        self._api = ContentApi(auth, cache_path=kodiutils.get_cache_path())

    def test_programs(self):
        programs = self._api.get_programs()
        self.assertIsInstance(programs, list)
        self.assertIsInstance(programs[0], Program)

    # def test_categories(self):
    #     for channel in ['vier', 'vijf', 'zes']:
    #         categories = self._api.get_categories(channel)
    #     self.assertIsInstance(categories, list)
    #     if categories:
    #         self.assertIsInstance(categories[0], Category)

    def test_episodes(self):
        for program in ['auwch', 'zo-man-zo-vrouw']:
            program = self._api.get_program(program, cache=CACHE_PREVENT)
            self.assertIsInstance(program, Program)
            self.assertIsInstance(program.seasons, dict)
            self.assertIsInstance(program.episodes, list)
            self.assertIsInstance(program.episodes[0], Episode)

    def test_clips(self):
        for program in ['gert-late-night']:
            program = self._api.get_program(program, extract_clips=True, cache=CACHE_PREVENT)

            self.assertIsInstance(program.clips, list)
            self.assertIsInstance(program.clips[0], Episode)

            episode = self._api.get_episode(program.clips[0].path, cache=CACHE_PREVENT)
            self.assertIsInstance(episode, Episode)

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_get_stream(self):
        program = self._api.get_program('auwch')
        self.assertIsInstance(program, Program)

        episode = program.episodes[0]
        resolved_stream = self._api.get_stream_by_uuid(episode.uuid)
        self.assertIsInstance(resolved_stream, ResolvedStream)

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_get_drm_stream(self):
        resolved_stream = self._api.get_stream_by_uuid('a545bb4f-0f4c-4588-92a2-5086041c0e08')  # Hawaii Five-O 8x12
        self.assertIsInstance(resolved_stream, ResolvedStream)


if __name__ == '__main__':
    unittest.main()
