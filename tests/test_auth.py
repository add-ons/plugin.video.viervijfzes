# -*- coding: utf-8 -*-
""" Tests for AUTH API """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

from resources.lib import kodiutils
from resources.lib.viervijfzes.auth import AuthApi
from resources.lib.viervijfzes.aws.cognito_identity import CognitoIdentity
from resources.lib.viervijfzes.aws.cognito_sync import CognitoSync

_LOGGER = logging.getLogger(__name__)


class TestAuth(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAuth, self).__init__(*args, **kwargs)

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_login(self):
        auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())

        # Clear any cache we have
        auth.clear_tokens()

        # We should get a token by logging in
        id_token = auth.get_token()
        self.assertTrue(id_token)

        # Test it a second time, it should go from memory now
        id_token = auth.get_token()
        self.assertTrue(id_token)

        # Test Cognito Identity
        identity_client = CognitoIdentity(AuthApi.COGNITO_POOL_ID, AuthApi.COGNITO_IDENTITY_POOL_ID)
        identity_id = identity_client.get_id(id_token)
        self.assertTrue(identity_id)

        credentials = identity_client.get_credentials_for_identity(id_token, identity_id)
        self.assertTrue(credentials)

        # Test Cognito Sync
        sync_client = CognitoSync(AuthApi.COGNITO_IDENTITY_POOL_ID, identity_id, credentials)
        dataset = sync_client.list_records('myList')
        self.assertTrue(dataset)


if __name__ == '__main__':
    unittest.main()
