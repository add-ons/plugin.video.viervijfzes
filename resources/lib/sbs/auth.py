# -*- coding: utf-8 -*-
""" AUTH API """

from __future__ import absolute_import, division, unicode_literals


class SbsAuth:
    COGNITO_REGION = 'eu-west-1'
    COGNITO_POOL_ID = 'eu-west-1_dViSsKM5Y'
    COGNITO_CLIENT_ID = '6s1h851s8uplco5h6mqh1jac8m'

    def __init__(self, username, password):
        """ Initialise object """
        self._username = username
        self._password = password

    def get_token(self):
        """ Returns an authentication token """
        import boto3
        from warrant.aws_srp import AWSSRP

        client = boto3.client('cognito-idp',
                              region_name=self.COGNITO_REGION,
                              aws_access_key_id='',
                              aws_secret_access_key='')

        aws = AWSSRP(username=self._username,
                     password=self._password,
                     pool_id=self.COGNITO_POOL_ID,
                     client_id=self.COGNITO_CLIENT_ID,
                     client=client)

        result = aws.authenticate_user()

        return result.get('AuthenticationResult', {}).get('IdToken')
