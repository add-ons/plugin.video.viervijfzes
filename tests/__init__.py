# -*- coding: utf-8 -*-
""" Tests """

from __future__ import absolute_import, division, unicode_literals

import logging
import os

import xbmcaddon

logging.basicConfig()

# Set credentials based on environment data
if os.environ.get('ADDON_USERNAME') and os.environ.get('ADDON_PASSWORD'):
    ADDON = xbmcaddon.Addon()
    ADDON.setSetting('username', os.environ.get('ADDON_USERNAME'))
    ADDON.setSetting('password', os.environ.get('ADDON_PASSWORD'))
