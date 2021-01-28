# -*- coding: utf-8 -*-
""" SBS API """
from __future__ import absolute_import, division, unicode_literals

from collections import OrderedDict

CHANNELS = OrderedDict([
    ('Play4', dict(
        name='Play 4',
        epg_id='vier',
        url='https://www.goplay.be',
        logo='play4.png',
        background='play4-background.png',
        iptv_preset=4,
        iptv_id='play4.be',
        youtube=[
            dict(
                label='VIER / VIJF',
                logo='vier.png',
                path='plugin://plugin.video.youtube/user/viertv/',
            ),
        ],
    )),
    ('Play5', dict(
        name='Play 5',
        epg_id='vijf',
        url='https://www.goplay.be',
        logo='play5.png',
        background='play5-background.png',
        iptv_preset=5,
        iptv_id='play5.be',
        youtube=[
            dict(
                label='VIER / VIJF',
                logo='vijf.png',
                path='plugin://plugin.video.youtube/user/viertv/',
            ),
        ],
    )),
    ('Play6', dict(
        name='Play 6',
        epg_id='zes',
        url='https://www.goplay.be',
        logo='play6.png',
        background='play6-background.png',
        iptv_preset=6,
        iptv_id='play6.be',
        youtube=[],
    )),
    # ('play7', dict(
    #     name='Play 7',
    #     url='https://www.goplay.be',
    #     logo='play7.png',
    #     background='play7-background.png',
    #     iptv_preset=7,
    #     iptv_id='play7.be',
    #     youtube=[],
    # )),
    ('GoPlay', dict(
        name='Go Play',
        url='https://www.goplay.be',
        logo='goplay.png',
        background='goplay-background.jpg',
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
