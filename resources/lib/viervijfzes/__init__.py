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
        youtube=[],
    ))
])

STREAM_DICT = {
    'codec': 'h264',
    'height': 544,
    'width': 960,
}
