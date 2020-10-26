# -*- coding: utf-8 -*-
""" Metadata module """

from __future__ import absolute_import, division, unicode_literals

from resources.lib import kodiutils
from resources.lib.viervijfzes import CHANNELS
from resources.lib.viervijfzes.content import CACHE_AUTO, CACHE_PREVENT, ContentApi, Program


class Metadata:
    """ Code responsible for the management of the local cached metadata """

    def __init__(self):
        """ Initialise object """
        self._api = ContentApi(cache_path=kodiutils.get_cache_path())

    def update(self):
        """ Update the metadata with a foreground progress indicator """
        # Create progress indicator
        progress = kodiutils.progress(message=kodiutils.localize(30715))  # Updating metadata...

        def update_status(i, total):
            """ Update the progress indicator """
            progress.update(int(((i + 1) / total) * 100),
                            kodiutils.localize(30716, index=i + 1, total=total))  # Updating metadata ({index}/{total})...
            return progress.iscanceled()

        self.fetch_metadata(callback=update_status, refresh=True)

        # Close progress indicator
        progress.close()

    def fetch_metadata(self, callback=None, refresh=False):
        """ Fetch the metadata for all the items in the catalog
        :type callback: callable
        :type refresh: bool
        """
        # Fetch all items from the catalog
        items = []
        for channel in list(CHANNELS):
            items.extend(self._api.get_programs(channel, CACHE_PREVENT))
        count = len(items)

        # Loop over all of them and download the metadata
        for index, item in enumerate(items):
            if isinstance(item, Program):
                self._api.get_program(item.channel, item.path, CACHE_PREVENT if refresh else CACHE_AUTO)

            # Run callback after every item
            if callback and callback(index, count):
                # Stop when callback returns True
                return False

        return True

    @staticmethod
    def clean():
        """ Clear metadata (called from settings) """
        cache_path = kodiutils.get_cache_path()
        _, files = kodiutils.listdir(cache_path)
        for filename in files:
            kodiutils.delete(cache_path + filename)

        kodiutils.set_setting('metadata_last_updated', '0')
        kodiutils.ok_dialog(message=kodiutils.localize(30714))  # Local metadata is cleared
