# -*- coding: utf-8 -*-
""" Search module """

from __future__ import absolute_import, division, unicode_literals

import logging

from resources.lib import kodiutils
from resources.lib.viervijfzes.auth import AuthApi
from resources.lib.viervijfzes.content import ContentApi

_LOGGER = logging.getLogger('search')


class Search:
    """ Menu code related to search """

    def __init__(self):
        """ Initialise object """
        self._auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())
        self._api = ContentApi(self._auth.get_token())

    def show_search(self, query=None):
        """ Shows the search dialog
        :type query: str
        """
        if not query:
            # Ask for query
            query = kodiutils.get_search_string(heading=kodiutils.localize(30009))  # Search Vier/Vijf/Zes
            if not query:
                kodiutils.end_of_directory()
                return

        # Do search
        try:
            items = self._vtm_go.do_search(query)
        except Exception as ex:  # pylint: disable=broad-except
            kodiutils.show_notification(message=str(ex))
            kodiutils.end_of_directory()
            return

        # Display results
        listing = []
        for item in items:
            listing.append(self._menu.generate_titleitem(item))

        # Sort like we get our results back.
        kodiutils.show_listing(listing, 30009, content='tvshows')
