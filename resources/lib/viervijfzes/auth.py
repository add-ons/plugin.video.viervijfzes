# -*- coding: utf-8 -*-
""" AUTH API """

from __future__ import absolute_import, division, unicode_literals

import json
import logging
import time

from resources.lib import kodiutils
from resources.lib.viervijfzes.auth_awsidp import AwsIdp, InvalidLoginException, AuthenticationException

_LOGGER = logging.getLogger('auth-api')


class AuthApi:
    """ VIER/VIJF/ZES Authentication API """
    COGNITO_REGION = 'eu-west-1'
    COGNITO_POOL_ID = 'eu-west-1_dViSsKM5Y'
    COGNITO_CLIENT_ID = '6s1h851s8uplco5h6mqh1jac8m'

    TOKEN_FILE = 'auth-tokens.json'

    def __init__(self, username, password):
        """ Initialise object """
        self._username = username
        self._password = password
        self._cache_dir = kodiutils.get_tokens_path()
        self._id_token = None
        self._expiry = 0
        self._refresh_token = None

        # Load tokens from cache
        try:
            with kodiutils.open_file(self._cache_dir + self.TOKEN_FILE, 'rb') as fdesc:
                data_json = json.loads(fdesc.read())
                self._id_token = data_json.get('id_token')
                self._refresh_token = data_json.get('refresh_token')
                self._expiry = int(data_json.get('expiry', 0))
        except (IOError, TypeError, ValueError):
            _LOGGER.info('We could not use the cache since it is invalid or non-existent.')

    def get_token(self):
        """ Get a valid token """
        now = int(time.time())

        if self._id_token and self._expiry > now:
            # We have a valid id token in memory, use it
            _LOGGER.debug('Got an id token from memory')
            return self._id_token

        if self._refresh_token:
            # We have a valid refresh token, use that to refresh our id token
            # The refresh token is valid for 30 days. If this refresh fails, we just continue by logging in again.
            _LOGGER.debug('Getting an id token by refreshing')
            try:
                self._id_token = self._refresh(self._refresh_token)
                self._expiry = now + 3600
            except (InvalidLoginException, AuthenticationException) as exc:
                _LOGGER.error('Error logging in: %s', str(exc))
                self._id_token = None
                self._refresh_token = None
                self._expiry = 0
                # We continue by logging in with username and password

        if not self._id_token:
            # We have no tokens, or they are all invalid, do a login
            _LOGGER.debug('Getting an id token by logging in')
            id_token, refresh_token = self._authenticate(self._username, self._password)
            self._id_token = id_token
            self._refresh_token = refresh_token
            self._expiry = now + 3600

        # Store new tokens in cache
        if not kodiutils.exists(self._cache_dir):
            kodiutils.mkdirs(self._cache_dir)
        with kodiutils.open_file(self._cache_dir + self.TOKEN_FILE, 'wb') as fdesc:
            data = json.dumps(dict(
                id_token=self._id_token,
                refresh_token=self._refresh_token,
                expiry=self._expiry,
            ))
            fdesc.write(data.encode('utf8'))

        return self._id_token

    @staticmethod
    def clear_tokens():
        """ Remove the cached tokens. """
        kodiutils.delete(kodiutils.get_tokens_path() + AuthApi.TOKEN_FILE)

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
