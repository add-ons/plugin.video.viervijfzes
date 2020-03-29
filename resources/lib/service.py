# -*- coding: utf-8 -*-
""" Background service code """

from __future__ import absolute_import, division, unicode_literals

import hashlib
import logging
import os
from time import time

from xbmc import Monitor

from resources.lib import kodilogging, kodiutils
from resources.lib.viervijfzes.auth import AuthApi

kodilogging.config()
_LOGGER = logging.getLogger('service')


class BackgroundService(Monitor):
    """ Background service code """

    def __init__(self):
        Monitor.__init__(self)
        self.update_interval = 24 * 3600  # Every 24 hours
        self.cache_expiry = 30 * 24 * 3600  # One month
        self._auth = AuthApi(kodiutils.get_setting('username'), kodiutils.get_setting('password'), kodiutils.get_tokens_path())

    def run(self):
        """ Background loop for maintenance tasks """
        _LOGGER.info('Service started')

        while not self.abortRequested():
            # Update every `update_interval` after the last update
            if kodiutils.get_setting_bool('metadata_update') and int(kodiutils.get_setting('metadata_last_updated', 0)) + self.update_interval < time():
                self._update_metadata()

            # Stop when abort requested
            if self.waitForAbort(10):
                break

        _LOGGER.info('Service stopped')

    def onSettingsChanged(self):  # pylint: disable=invalid-name
        """ Callback when a setting has changed """
        if self._has_credentials_changed():
            _LOGGER.info('Clearing auth tokens due to changed credentials')
            self._auth.clear_tokens()

            # Refresh container
            kodiutils.container_refresh()

    @staticmethod
    def _has_credentials_changed():
        """ Check if credentials have changed """
        old_hash = kodiutils.get_setting('credentials_hash')
        new_hash = ''
        if kodiutils.get_setting('username') or kodiutils.get_setting('password'):
            new_hash = hashlib.md5((kodiutils.get_setting('username') + kodiutils.get_setting('password')).encode('utf-8')).hexdigest()
        if new_hash != old_hash:
            kodiutils.set_setting('credentials_hash', new_hash)
            return True
        return False

    def _update_metadata(self):
        """ Update the metadata for the listings """
        from resources.lib.modules.metadata import Metadata

        def update_status(_i, _total):
            """ Allow to cancel the background job """
            return self.abortRequested() or not kodiutils.get_setting_bool('metadata_update')

        # Clear metadata that has expired for 30 days
        self._remove_expired_metadata(30 * 24 * 60 * 60)

        # Fetch new metadata
        success = Metadata().fetch_metadata(callback=update_status)

        # Update metadata_last_updated
        if success:
            kodiutils.set_setting('metadata_last_updated', str(int(time())))

    @staticmethod
    def _remove_expired_metadata(keep_expired=None):
        """ Clear the cache """
        path = kodiutils.get_cache_path()
        if not os.path.exists(path):
            return

        now = time()
        for filename in os.listdir(path):
            fullpath = path + filename
            if keep_expired and os.stat(fullpath).st_mtime + keep_expired > now:
                continue
            os.unlink(fullpath)


def run():
    """ Run the BackgroundService """
    BackgroundService().run()
