# -*- coding: utf-8 -*-
"""Addon entry point"""

from __future__ import absolute_import, division, unicode_literals

import xbmcaddon

from resources.lib import kodiutils

kodiutils.ADDON = xbmcaddon.Addon()

if __name__ == '__main__':
    from sys import argv
    from resources.lib.addon import run

    run(argv)
