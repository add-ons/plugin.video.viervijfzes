# -*- coding: utf-8 -*-
""" AUTH API """

from __future__ import absolute_import, division, unicode_literals

import json
import logging
from datetime import datetime

from resources.lib.sbs.auth_awsidp import AwsIdp

_LOGGER = logging.getLogger('auth')


class AuthApi:
    """ Vier/Vijf/Zes Authentication API """
    COGNITO_REGION = 'eu-west-1'
    COGNITO_POOL_ID = 'eu-west-1_dViSsKM5Y'
    COGNITO_CLIENT_ID = '6s1h851s8uplco5h6mqh1jac8m'

    def __init__(self, username, password, cache=None):
        """ Initialise object """
        self._username = username
        self._password = password
        self._cache = cache
        self._id_token = None
        self._expiry = 0
        self._refresh_token = None

        if self._cache:
            # Load tokens from cache
            try:
                with open(self._cache, 'r') as f:
                    data_json = json.loads(f.read())
                    self._id_token = data_json.get('id_token')
                    self._refresh_token = data_json.get('refresh_token')
                    self._expiry = int(data_json.get('expiry', 0))
            except (FileNotFoundError, TypeError):
                _LOGGER.info('We could not use the cache since it is invalid or non-existant.')

    def get_token(self):
        """ Get a valid token """
        now = int(datetime.today().timestamp())

        if self._id_token and self._expiry > now:
            # We have a valid id token in memory, use it
            _LOGGER.debug('Got an id token from memory: %s', self._id_token)
            return self._id_token

        if self._refresh_token:
            # We have a valid refresh token, use that to refresh our id token
            # The refresh token is valid for 30 days. If this refresh fails, we just continue by logging in again.
            self._id_token = self._refresh(self._refresh_token)
            if self._id_token:
                self._expiry = now + 3600
                _LOGGER.debug('Got an id token by refreshing: %s', self._id_token)

        if not self._id_token:
            # We have no tokens, or they are all invalid, do a login
            id_token, refresh_token = self._authenticate(self._username, self._password)
            self._id_token = id_token
            self._refresh_token = refresh_token
            self._expiry = now + 3600
            _LOGGER.debug('Got an id token by logging in: %s', self._id_token)

        if self._cache:
            # Store new tokens in cache
            with open(self._cache, 'w') as f:
                f.write(json.dumps(dict(
                    id_token=self._id_token,
                    refresh_token=self._refresh_token,
                    expiry=self._expiry,
                )))

        return self._id_token

    @staticmethod
    def _authenticate(username, password):
        """ Authenticate with Amazon Cognito and fetch a refresh token and id token. """
        client = AwsIdp(AuthApi.COGNITO_POOL_ID, AuthApi.COGNITO_CLIENT_ID)
        return client.authenticate(username, password)

    @staticmethod
    def _refresh(refresh_token):
        """ Use the refresh token to fetch a new id token. """
        client = AwsIdp(AuthApi.COGNITO_POOL_ID, AuthApi.COGNITO_CLIENT_ID)
        return client.renew_token(refresh_token)
