# -*- coding: utf-8 -*-
""" AUTH API """

from __future__ import absolute_import, division, unicode_literals

import json
import logging

import requests

from resources.lib.viervijfzes.content import Program

_LOGGER = logging.getLogger('search-api')


class SearchApi:
    """ VIER/VIJF/ZES Search API """
    API_ENDPOINT = 'https://api.viervijfzes.be/search'

    def __init__(self):
        """ Initialise object """
        self._session = requests.session()

    def search(self, query):
        """ Get the stream URL to use for this video.
        :type query: str
        :rtype list[Program]
        """
        if not query:
            return []

        response = self._session.post(
            self.API_ENDPOINT,
            json={
                "query": query,
                "sites": ["vier", "vijf", "zes"],
                "page": 0,
                "mode": "byDate"
            }
        )

        if response.status_code != 200:
            raise Exception('Could not search')

        data = json.loads(response.text)

        results = []
        for hit in data['hits']['hits']:
            if hit['_source']['bundle'] == 'program':
                results.append(Program(
                    channel=hit['_source']['site'],
                    path=hit['_source']['url'].strip('/'),
                    title=hit['_source']['title'],
                    description=hit['_source']['intro'],
                    cover=hit['_source']['img'],
                ))

        return results
