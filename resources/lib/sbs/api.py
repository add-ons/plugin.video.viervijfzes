# -*- coding: utf-8 -*-
""" AUTH API """

from __future__ import absolute_import, division, unicode_literals

import json
import logging

import requests

_LOGGER = logging.getLogger('api')


class SbsApi:
    API_ENDPOINT = 'https://api.viervijfzes.be'

    def __init__(self, token):
        """ Initialise object """
        self._token = token

        self._session = requests.session()
        self._session.headers['authorization'] = token

    def get_notifications(self):
        """ Get a list of notifications for your account. """
        response = self._get_url(self.API_ENDPOINT + '/notifications')
        data = json.loads(response)
        return data

    def _get_url(self, url, params=None):
        """ Makes a GET request for the specified URL.
        :type url: str
        :rtype str
        """
        response = self._session.get(url, params=params)
        return response.text
