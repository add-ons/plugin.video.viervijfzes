# -*- coding: utf-8 -*-
"""Episode Downloader"""

from __future__ import absolute_import, division, unicode_literals

import logging
import re
import subprocess

_LOGGER = logging.getLogger('downloader')


class Downloader:
    """ Allows to download an episode to disk for caching purposes. """

    def __init__(self):
        pass

    @staticmethod
    def check():
        """ Check if we have ffmpeg installed."""
        try:
            proc = subprocess.Popen(['ffmpeg', '-version'], stderr=subprocess.PIPE)
        except OSError:
            return False

        # Wait for the process to finish
        output = proc.stderr.readlines()
        proc.wait()

        # Check error code
        if proc.returncode != 0:
            _LOGGER.error(output)
            return False

        # TODO: Check version
        _LOGGER.debug('Output: %s', output)

        return True

    @staticmethod
    def download(stream, output, progress_callback=None):
        """Download the stream to destination."""
        try:
            cmd = ['ffmpeg', '-y', '-loglevel', 'info', '-i', stream, '-codec', 'copy', output]
            # `universal_newlines` makes proc.stderr.readline() also work on \r
            proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
        except OSError:
            return False

        regex_total = re.compile(r"Duration: (\d{2}):(\d{2}):(\d{2})")
        regex_current = re.compile(r"time=(\d{2}):(\d{2}):(\d{2})")

        # Keep looping over ffmpeg output
        total = None
        while True:
            line = proc.stderr.readline()
            if not line:
                break

            _LOGGER.debug('ffmpeg output: %s', line.rstrip())

            # Read the current status that is printed every few seconds.
            match = regex_current.search(line)
            if match and progress_callback:
                cancel = progress_callback(total, int(match.group(1)) * 3600 + int(match.group(2)) * 60 + int(match.group(3)))
                if cancel:
                    proc.terminate()
                continue

            # Read the total stream duration if we haven't found it already. It's there somewhere in the output. We'll find it.
            if not total:
                match = regex_total.search(line)
                if match:
                    total = int(match.group(1)) * 3600 + int(match.group(2)) * 60 + int(match.group(3))

        # Wait for ffmpeg to be fully finished
        proc.wait()

        # Check error code
        if proc.returncode != 0:
            return False

        return True
