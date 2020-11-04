# -*- coding: utf-8 -*-
""" SBS API """
from __future__ import absolute_import, division, unicode_literals

from collections import OrderedDict

CHANNELS = OrderedDict([
    ('vier', dict(
        name='VIER',
        url='https://www.vier.be',
        logo='vier.png',
        background='vier-background.jpg',
        studio_icon='vier',
        iptv_preset=4,
        iptv_id='vier.be',
        youtube=[
            dict(
                label='VIER / VIJF',
                logo='vier.png',
                path='plugin://plugin.video.youtube/user/viertv/',
            ),
        ],
    )),
    ('vijf', dict(
        name='VIJF',
        url='https://www.vijf.be',
        logo='vijf.png',
        background='vijf-background.jpg',
        studio_icon='vijf',
        iptv_preset=5,
        iptv_id='vijf.be',
        youtube=[
            dict(
                label='VIER / VIJF',
                logo='vijf.png',
                path='plugin://plugin.video.youtube/user/viertv/',
            ),
        ],
    )),
    ('zes', dict(
        name='ZES',
        url='https://www.zestv.be',
        logo='zes.png',
        background='zes-background.jpg',
        studio_icon='zes',
        iptv_preset=6,
        iptv_id='zes.be',
        youtube=[],
    ))
])

STREAM_DICT = {
    'codec': 'h264',
    'height': 544,
    'width': 960,
}


class ResolvedStream:
    """ Defines a stream that we can play"""

    def __init__(self, uuid=None, url=None, stream_type=None, license_url=None, auth=None):
        """
        :type uuid: str
        :type url: str
        :type stream_type: str
        :type license_url: str
        :type auth: str
        """
        self.uuid = uuid
        self.url = url
        self.stream_type = stream_type
        self.license_url = license_url
        self.auth = auth

    def __repr__(self):
        return "%r" % self.__dict__
