# -*- coding: utf-8 -*-
"""All functionality that requires Kodi imports"""

from __future__ import absolute_import, division, unicode_literals

import logging
from contextlib import contextmanager

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

ADDON = xbmcaddon.Addon()

SORT_METHODS = dict(
    unsorted=xbmcplugin.SORT_METHOD_UNSORTED,
    label=xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS,
    title=xbmcplugin.SORT_METHOD_TITLE,
    episode=xbmcplugin.SORT_METHOD_EPISODE,
    duration=xbmcplugin.SORT_METHOD_DURATION,
    year=xbmcplugin.SORT_METHOD_VIDEO_YEAR,
    date=xbmcplugin.SORT_METHOD_DATE,
)
DEFAULT_SORT_METHODS = [
    'unsorted', 'title'
]

_LOGGER = logging.getLogger('kodiutils')


class TitleItem:
    """ This helper object holds all information to be used with Kodi xbmc's ListItem object """

    def __init__(self, title, path=None, art_dict=None, info_dict=None, prop_dict=None, stream_dict=None, context_menu=None, subtitles_path=None,
                 is_playable=False):
        """ The constructor for the TitleItem class
        :type title: str
        :type path: str
        :type art_dict: dict
        :type info_dict: dict
        :type prop_dict: dict
        :type stream_dict: dict
        :type context_menu: list[tuple[str, str]]
        :type subtitles_path: list[str]
        :type is_playable: bool
        """
        self.title = title
        self.path = path
        self.art_dict = art_dict
        self.info_dict = info_dict
        self.stream_dict = stream_dict
        self.prop_dict = prop_dict
        self.context_menu = context_menu
        self.subtitles_path = subtitles_path
        self.is_playable = is_playable

    def __repr__(self):
        return "%r" % self.__dict__


class SafeDict(dict):
    """A safe dictionary implementation that does not break down on missing keys"""

    def __missing__(self, key):
        """Replace missing keys with the original placeholder"""
        return '{' + key + '}'


def to_unicode(text, encoding='utf-8', errors='strict'):
    """Force text to unicode"""
    if isinstance(text, bytes):
        return text.decode(encoding, errors=errors)
    return text


def from_unicode(text, encoding='utf-8', errors='strict'):
    """Force unicode to text"""
    import sys
    if sys.version_info.major == 2 and isinstance(text, unicode):  # noqa: F821; pylint: disable=undefined-variable
        return text.encode(encoding, errors)
    return text


def addon_icon():
    """Cache and return add-on icon"""
    return get_addon_info('icon')


def addon_id():
    """Cache and return add-on ID"""
    return get_addon_info('id')


def addon_fanart():
    """Cache and return add-on fanart"""
    return get_addon_info('fanart')


def addon_name():
    """Cache and return add-on name"""
    return get_addon_info('name')


def addon_path():
    """Cache and return add-on path"""
    return get_addon_info('path')


def addon_profile():
    """Cache and return add-on profile"""
    return to_unicode(xbmc.translatePath(ADDON.getAddonInfo('profile')))


def url_for(name, *args, **kwargs):
    """Wrapper for routing.url_for() to lookup by name"""
    import resources.lib.addon as addon
    return addon.routing.url_for(getattr(addon, name), *args, **kwargs)


def show_listing(title_items, category=None, sort=None, content=None, cache=True):
    """ Show a virtual directory in Kodi """
    from resources.lib.addon import routing

    if content:
        # content is one of: files, songs, artists, albums, movies, tvshows, episodes, musicvideos, videos, images, games
        xbmcplugin.setContent(routing.handle, content=content)

    # Jump through hoops to get a stable breadcrumbs implementation
    category_label = ''
    if category:
        if not content:
            category_label = addon_name() + ' / '
        if isinstance(category, int):
            category_label += localize(category)
        else:
            category_label += category
    elif not content:
        category_label = addon_name()

    xbmcplugin.setPluginCategory(handle=routing.handle, category=category_label)

    # Add all sort methods to GUI (start with preferred)
    if sort is None:
        sort = DEFAULT_SORT_METHODS
    elif not isinstance(sort, list):
        sort = [sort] + DEFAULT_SORT_METHODS

    for key in sort:
        xbmcplugin.addSortMethod(handle=routing.handle, sortMethod=SORT_METHODS[key])

    # Add the listings
    listing = []
    for title_item in title_items:
        # Three options:
        #  - item is a virtual directory/folder (not playable, path)
        #  - item is a playable file (playable, path)
        #  - item is non-actionable item (not playable, no path)
        is_folder = bool(not title_item.is_playable and title_item.path)
        is_playable = bool(title_item.is_playable and title_item.path)

        list_item = xbmcgui.ListItem(label=title_item.title, path=title_item.path)

        if title_item.prop_dict:
            list_item.setProperties(title_item.prop_dict)
        list_item.setProperty(key='IsPlayable', value='true' if is_playable else 'false')

        list_item.setIsFolder(is_folder)

        if title_item.art_dict:
            list_item.setArt(title_item.art_dict)

        if title_item.info_dict:
            # type is one of: video, music, pictures, game
            list_item.setInfo(type='video', infoLabels=title_item.info_dict)

        if title_item.stream_dict:
            # type is one of: video, audio, subtitle
            list_item.addStreamInfo('video', title_item.stream_dict)

        if title_item.context_menu:
            list_item.addContextMenuItems(title_item.context_menu)

        is_folder = bool(not title_item.is_playable and title_item.path)
        url = title_item.path if title_item.path else None
        listing.append((url, list_item, is_folder))

    succeeded = xbmcplugin.addDirectoryItems(routing.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(routing.handle, succeeded, cacheToDisc=cache)


def play(stream, title=None, art_dict=None, info_dict=None, prop_dict=None):
    """Play the given stream"""
    from resources.lib.addon import routing

    play_item = xbmcgui.ListItem(label=title, path=stream)
    if art_dict:
        play_item.setArt(art_dict)
    if info_dict:
        play_item.setInfo(type='video', infoLabels=info_dict)
    if prop_dict:
        play_item.setProperties(prop_dict)

    xbmcplugin.setResolvedUrl(routing.handle, True, listitem=play_item)


def get_search_string(heading='', message=''):
    """ Ask the user for a search string """
    search_string = None
    keyboard = xbmc.Keyboard(message, heading)
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_string = to_unicode(keyboard.getText())
    return search_string


def ok_dialog(heading='', message=''):
    """Show Kodi's OK dialog"""
    from xbmcgui import Dialog
    if not heading:
        heading = addon_name()
    return Dialog().ok(heading=heading, line1=message)


def yesno_dialog(heading='', message='', nolabel=None, yeslabel=None):
    """Show Kodi's OK dialog"""
    from xbmcgui import Dialog
    if not heading:
        heading = addon_name()
    return Dialog().yesno(heading=heading, line1=message, nolabel=nolabel, yeslabel=yeslabel)


def notification(heading='', message='', icon='info', time=4000):
    """Show a Kodi notification"""
    from xbmcgui import Dialog
    if not heading:
        heading = addon_name()
    if not icon:
        icon = addon_icon()
    Dialog().notification(heading=heading, message=message, icon=icon, time=time)


def multiselect(heading='', options=None, autoclose=0, preselect=None, use_details=False):
    """Show a Kodi multi-select dialog"""
    from xbmcgui import Dialog
    if not heading:
        heading = addon_name()
    return Dialog().multiselect(heading=heading, options=options, autoclose=autoclose, preselect=preselect, useDetails=use_details)


def progress(heading='', message=''):
    """ Show a Kodi progress dialog """
    from xbmcgui import DialogProgress
    if not heading:
        heading = ADDON.getAddonInfo('name')
    dialog_progress = DialogProgress()
    dialog_progress.create(heading=heading, line1=message)
    return dialog_progress


def set_locale():
    """Load the proper locale for date strings, only once"""
    if hasattr(set_locale, 'cached'):
        return getattr(set_locale, 'cached')
    from locale import Error, LC_ALL, setlocale
    locale_lang = get_global_setting('locale.language').split('.')[-1]
    locale_lang = locale_lang[:-2] + locale_lang[-2:].upper()
    # NOTE: setlocale() only works if the platform supports the Kodi configured locale
    try:
        setlocale(LC_ALL, locale_lang)
    except (Error, ValueError) as exc:
        if locale_lang != 'en_GB':
            _LOGGER.debug("Your system does not support locale '%s': %s", locale_lang, exc)
            set_locale.cached = False
            return False
    set_locale.cached = True
    return True


def localize(string_id, **kwargs):
    """Return the translated string from the .po language files, optionally translating variables"""
    if kwargs:
        from string import Formatter
        return Formatter().vformat(ADDON.getLocalizedString(string_id), (), SafeDict(**kwargs))
    return ADDON.getLocalizedString(string_id)


def get_setting(key, default=None):
    """Get an add-on setting as string"""
    try:
        value = to_unicode(ADDON.getSetting(key))
    except RuntimeError:  # Occurs when the add-on is disabled
        return default
    if value == '' and default is not None:
        return default
    return value


def get_setting_bool(key, default=None):
    """Get an add-on setting as boolean"""
    try:
        return ADDON.getSettingBool(key)
    except (AttributeError, TypeError):  # On Krypton or older, or when not a boolean
        value = get_setting(key, default)
        if value not in ('false', 'true'):
            return default
        return bool(value == 'true')
    except RuntimeError:  # Occurs when the add-on is disabled
        return default


def get_setting_int(key, default=None):
    """Get an add-on setting as integer"""
    try:
        return ADDON.getSettingInt(key)
    except (AttributeError, TypeError):  # On Krypton or older, or when not an integer
        value = get_setting(key, default)
        try:
            return int(value)
        except ValueError:
            return default
    except RuntimeError:  # Occurs when the add-on is disabled
        return default


def get_setting_float(key, default=None):
    """Get an add-on setting"""
    try:
        return ADDON.getSettingNumber(key)
    except (AttributeError, TypeError):  # On Krypton or older, or when not a float
        value = get_setting(key, default)
        try:
            return float(value)
        except ValueError:
            return default
    except RuntimeError:  # Occurs when the add-on is disabled
        return default


def set_setting(key, value):
    """Set an add-on setting"""
    return ADDON.setSetting(key, from_unicode(str(value)))


def set_setting_bool(key, value):
    """Set an add-on setting as boolean"""
    try:
        return ADDON.setSettingBool(key, value)
    except (AttributeError, TypeError):  # On Krypton or older, or when not a boolean
        if value in ['false', 'true']:
            return set_setting(key, value)
        if value:
            return set_setting(key, 'true')
        return set_setting(key, 'false')


def set_setting_int(key, value):
    """Set an add-on setting as integer"""
    try:
        return ADDON.setSettingInt(key, value)
    except (AttributeError, TypeError):  # On Krypton or older, or when not an integer
        return set_setting(key, value)


def set_setting_float(key, value):
    """Set an add-on setting"""
    try:
        return ADDON.setSettingNumber(key, value)
    except (AttributeError, TypeError):  # On Krypton or older, or when not a float
        return set_setting(key, value)


def open_settings():
    """Open the add-in settings window, shows Credentials"""
    ADDON.openSettings()


def get_global_setting(key):
    """Get a Kodi setting"""
    result = jsonrpc(method='Settings.GetSettingValue', params=dict(setting=key))
    return result.get('result', {}).get('value')


def set_global_setting(key, value):
    """Set a Kodi setting"""
    return jsonrpc(method='Settings.SetSettingValue', params=dict(setting=key, value=value))


def get_cond_visibility(condition):
    """Test a condition in XBMC"""
    return xbmc.getCondVisibility(condition)


def has_addon(name):
    """Checks if add-on is installed"""
    return xbmc.getCondVisibility('System.HasAddon(%s)' % name) == 1


def kodi_version():
    """Returns major Kodi version"""
    return int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0])


def get_tokens_path():
    """Cache and return the userdata tokens path"""
    if not hasattr(get_tokens_path, 'cached'):
        get_tokens_path.cached = addon_profile() + 'tokens/'
    return getattr(get_tokens_path, 'cached')


def get_cache_path():
    """Cache and return the userdata cache path"""
    if not hasattr(get_cache_path, 'cached'):
        get_cache_path.cached = addon_profile() + 'cache/'
    return getattr(get_cache_path, 'cached')


def get_addon_info(key):
    """Return addon information"""
    return to_unicode(ADDON.getAddonInfo(key))


def listdir(path):
    """Return all files in a directory (using xbmcvfs)"""
    from xbmcvfs import listdir as vfslistdir
    return vfslistdir(path)


def mkdir(path):
    """Create a directory (using xbmcvfs)"""
    from xbmcvfs import mkdir as vfsmkdir
    _LOGGER.debug("Create directory '%s'.", path)
    return vfsmkdir(path)


def mkdirs(path):
    """Create directory including parents (using xbmcvfs)"""
    from xbmcvfs import mkdirs as vfsmkdirs
    _LOGGER.debug("Recursively create directory '%s'.", path)
    return vfsmkdirs(path)


def exists(path):
    """Whether the path exists (using xbmcvfs)"""
    from xbmcvfs import exists as vfsexists
    return vfsexists(path)


@contextmanager
def open_file(path, flags='r'):
    """Open a file (using xbmcvfs)"""
    from xbmcvfs import File
    fdesc = File(path, flags)
    yield fdesc
    fdesc.close()


def stat_file(path):
    """Return information about a file (using xbmcvfs)"""
    from xbmcvfs import Stat
    return Stat(path)


def delete(path):
    """Remove a file (using xbmcvfs)"""
    from xbmcvfs import delete as vfsdelete
    _LOGGER.debug("Delete file '%s'.", path)
    return vfsdelete(path)


def container_refresh(url=None):
    """Refresh the current container or (re)load a container by URL"""
    if url:
        _LOGGER.debug('Execute: Container.Refresh(%s)', url)
        xbmc.executebuiltin('Container.Refresh({url})'.format(url=url))
    else:
        _LOGGER.debug('Execute: Container.Refresh')
        xbmc.executebuiltin('Container.Refresh')


def container_update(url):
    """Update the current container while respecting the path history."""
    if url:
        _LOGGER.debug('Execute: Container.Update(%s)', url)
        xbmc.executebuiltin('Container.Update({url})'.format(url=url))
    else:
        # URL is a mandatory argument for Container.Update, use Container.Refresh instead
        container_refresh()


def end_of_directory():
    """Close a virtual directory, required to avoid a waiting Kodi"""
    from resources.lib.addon import routing
    xbmcplugin.endOfDirectory(handle=routing.handle, succeeded=False, updateListing=False, cacheToDisc=False)


def jsonrpc(*args, **kwargs):
    """Perform JSONRPC calls"""
    from json import dumps, loads

    # We do not accept both args and kwargs
    if args and kwargs:
        _LOGGER.error('Wrong use of jsonrpc()')
        return None

    # Process a list of actions
    if args:
        for (idx, cmd) in enumerate(args):
            if cmd.get('id') is None:
                cmd.update(id=idx)
            if cmd.get('jsonrpc') is None:
                cmd.update(jsonrpc='2.0')
        return loads(xbmc.executeJSONRPC(dumps(args)))

    # Process a single action
    if kwargs.get('id') is None:
        kwargs.update(id=0)
    if kwargs.get('jsonrpc') is None:
        kwargs.update(jsonrpc='2.0')
    return loads(xbmc.executeJSONRPC(dumps(kwargs)))


def get_cache(key, ttl=None):
    """ Get an item from the cache """
    import time
    path = get_cache_path()
    filename = '.'.join(key)
    fullpath = path + filename

    if not exists(fullpath):
        return None

    if ttl and time.mktime(time.localtime()) - stat_file(fullpath).st_mtime() > ttl:
        return None

    with open_file(fullpath, 'r') as fdesc:
        try:
            _LOGGER.debug('Fetching %s from cache', filename)
            import json
            value = json.load(fdesc)
            return value
        except (ValueError, TypeError):
            return None


def set_cache(key, data):
    """ Store an item in the cache """
    path = get_cache_path()
    filename = '.'.join(key)
    fullpath = path + filename

    if not exists(path):
        mkdirs(path)

    with open_file(fullpath, 'w') as fdesc:
        _LOGGER.debug('Storing to cache as %s', filename)
        import json
        json.dump(data, fdesc)


def invalidate_cache(ttl=None):
    """ Clear the cache """
    path = get_cache_path()
    if not exists(path):
        return
    _, files = listdir(path)
    import time
    now = time.mktime(time.localtime())
    for filename in files:
        fullpath = path + filename
        if ttl and now - stat_file(fullpath).st_mtime() < ttl:
            continue
        delete(fullpath)
