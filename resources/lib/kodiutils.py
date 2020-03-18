# -*- coding: utf-8 -*-
"""All functionality that requires Kodi imports"""

from __future__ import absolute_import, division, unicode_literals

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

# from utils import from_unicode, to_unicode

ADDON = xbmcaddon.Addon()

SORT_METHODS = dict(
    unsorted=xbmcplugin.SORT_METHOD_UNSORTED,
    label=xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS,
    episode=xbmcplugin.SORT_METHOD_EPISODE,
    duration=xbmcplugin.SORT_METHOD_DURATION,
    year=xbmcplugin.SORT_METHOD_VIDEO_YEAR,
    date=xbmcplugin.SORT_METHOD_DATE,
)
DEFAULT_SORT_METHODS = [
    'unsorted', 'label'
]


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
    from resources.lib import addon
    return addon.routing.url_for(getattr(addon, name), *args, **kwargs)


def show_listing(title_items, category=None, sort=None, content=None, cache=True):
    """ Show a virtual directory in Kodi """

    from resources.lib import addon

    if content:
        # content is one of: files, songs, artists, albums, movies, tvshows, episodes, musicvideos, videos, images, games
        xbmcplugin.setContent(addon.routing.handle, content=content)

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

    xbmcplugin.setPluginCategory(handle=addon.routing.handle, category=category_label)

    # Add all sort methods to GUI (start with preferred)
    if sort is None:
        sort = DEFAULT_SORT_METHODS
    elif not isinstance(sort, list):
        sort = [sort] + DEFAULT_SORT_METHODS

    for key in sort:
        xbmcplugin.addSortMethod(handle=addon.routing.handle, sortMethod=SORT_METHODS[key])

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

    succeeded = xbmcplugin.addDirectoryItems(addon.routing.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(addon.routing.handle, succeeded, cacheToDisc=cache)


def play(stream, title=None, description=None, art_dict={}, info_dict={}, prop_dict={}):
    """ Play the given stream.
    """
    from resources.lib.addon import routing

    play_item = xbmcgui.ListItem(label=title, path=stream)
    # play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
    # play_item.setProperty('inputstream.adaptive.max_bandwidth', str(self.get_max_bandwidth() * 1000))
    # play_item.setProperty('network.bandwidth', str(self.get_max_bandwidth() * 1000))
    # play_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    # play_item.setMimeType('application/dash+xml')
    # play_item.setContentLookup(False)

    # if license_key is not None:
    #     play_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
    #     play_item.setProperty('inputstream.adaptive.license_key', license_key)

    # Note: Adding the subtitle directly on the ListItem could cause sync issues, therefore
    # we add the subtitles trough the Player after playback has started.
    # See https://github.com/michaelarnauts/plugin.video.vtm.go/issues/148
    # This is probably a Kodi or inputstream.adaptive issue

    # if title_item.subtitles_path:
    #     play_item.setSubtitles(title_item.subtitles_path)

    # To support video playback directly from RunPlugin() we need to use xbmc.Player().play instead of
    # setResolvedUrl that only works with PlayMedia() or with internal playable menu items
    xbmcplugin.setResolvedUrl(routing.handle, True, listitem=play_item)


def get_search_string(search_string=None):
    """Ask the user for a search string"""
    keyboard = xbmc.Keyboard(search_string, localize(30134))
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
            log(3, "Your system does not support locale '{locale}': {error}", locale=locale_lang, error=exc)
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


def localize_time(time):
    """Return localized time"""
    time_format = xbmc.getRegion('time').replace(':%S', '')  # Strip off seconds
    return time.strftime(time_format).lstrip('0')  # Remove leading zero on all platforms


def localize_date(date, strftime):
    """Return a localized date, even if the system does not support your locale"""
    has_locale = set_locale()
    # When locale is supported, return original format
    if has_locale:
        return date.strftime(strftime)
    # When locale is unsupported, translate weekday and month
    if '%A' in strftime:
        strftime = strftime.replace('%A', WEEKDAY_LONG[date.strftime('%w')])
    elif '%a' in strftime:
        strftime = strftime.replace('%a', WEEKDAY_SHORT[date.strftime('%w')])
    if '%B' in strftime:
        strftime = strftime.replace('%B', MONTH_LONG[date.strftime('%m')])
    elif '%b' in strftime:
        strftime = strftime.replace('%b', MONTH_SHORT[date.strftime('%m')])
    return date.strftime(strftime)


def localize_datelong(date):
    """Return a localized long date string"""
    return localize_date(date, xbmc.getRegion('datelong'))


def localize_from_data(name, data):
    """Return a localized name string from a Dutch data object"""
    # Return if Kodi language is Dutch
    if get_global_setting('locale.language') == 'resource.language.nl_nl':
        return name
    return next((localize(item.get('msgctxt')) for item in data if item.get('name') == name), name)


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


def get_advanced_setting(key, default=None):
    """Get a setting from advancedsettings.xml"""
    as_path = xbmc.translatePath('special://masterprofile/advancedsettings.xml')
    if not exists(as_path):
        return default
    from xml.etree.ElementTree import parse, ParseError
    try:
        as_root = parse(as_path).getroot()
    except ParseError:
        return default
    value = as_root.find(key)
    if value is not None:
        if value.text is None:
            return default
        return value.text
    return default


def get_advanced_setting_int(key, default=0):
    """Get a setting from advancedsettings.xml as an integer"""
    if not isinstance(default, int):
        default = 0
    setting = get_advanced_setting(key, default)
    if not isinstance(setting, int):
        setting = int(setting.strip()) if setting.strip().isdigit() else default
    return setting


def get_property(key, default=None, window_id=10000):
    """Get a Window property"""
    from xbmcgui import Window
    value = to_unicode(Window(window_id).getProperty(key))
    if value == '' and default is not None:
        return default
    return value


def set_property(key, value, window_id=10000):
    """Set a Window property"""
    from xbmcgui import Window
    return Window(window_id).setProperty(key, from_unicode(value))


def clear_property(key, window_id=10000):
    """Clear a Window property"""
    from xbmcgui import Window
    return Window(window_id).clearProperty(key)


def notify(sender, message, data):
    """Send a notification to Kodi using JSON RPC"""
    result = jsonrpc(method='JSONRPC.NotifyAll', params=dict(
        sender=sender,
        message=message,
        data=data,
    ))
    if result.get('result') != 'OK':
        log_error('Failed to send notification: {error}', error=result.get('error').get('message'))
        return False
    log(2, 'Succesfully sent notification')
    return True


def get_playerid():
    """Get current playerid"""
    result = dict()
    while not result.get('result'):
        result = jsonrpc(method='Player.GetActivePlayers')
    return result.get('result', [{}])[0].get('playerid')


def get_max_bandwidth():
    """Get the max bandwidth based on Kodi and add-on settings"""
    addon_max_bandwidth = get_setting_int('max_bandwidth', default=0)
    global_max_bandwidth = int(get_global_setting('network.bandwidth'))
    if addon_max_bandwidth != 0 and global_max_bandwidth != 0:
        return min(addon_max_bandwidth, global_max_bandwidth)
    if addon_max_bandwidth != 0:
        return addon_max_bandwidth
    if global_max_bandwidth != 0:
        return global_max_bandwidth
    return 0


def has_socks():
    """Test if socks is installed, and use a static variable to remember"""
    if hasattr(has_socks, 'cached'):
        return getattr(has_socks, 'cached')
    try:
        import socks  # noqa: F401; pylint: disable=unused-variable,unused-import
    except ImportError:
        has_socks.cached = False
        return None  # Detect if this is the first run
    has_socks.cached = True
    return True


def get_proxies():
    """Return a usable proxies dictionary from Kodi proxy settings"""
    usehttpproxy = get_global_setting('network.usehttpproxy')
    if usehttpproxy is not True:
        return None

    try:
        httpproxytype = int(get_global_setting('network.httpproxytype'))
    except ValueError:
        httpproxytype = 0

    socks_supported = has_socks()
    if httpproxytype != 0 and not socks_supported:
        # Only open the dialog the first time (to avoid multiple popups)
        if socks_supported is None:
            ok_dialog('', localize(30966))  # Requires PySocks
        return None

    proxy_types = ['http', 'socks4', 'socks4a', 'socks5', 'socks5h']

    proxy = dict(
        scheme=proxy_types[httpproxytype] if 0 <= httpproxytype < 5 else 'http',
        server=get_global_setting('network.httpproxyserver'),
        port=get_global_setting('network.httpproxyport'),
        username=get_global_setting('network.httpproxyusername'),
        password=get_global_setting('network.httpproxypassword'),
    )

    if proxy.get('username') and proxy.get('password') and proxy.get('server') and proxy.get('port'):
        proxy_address = '{scheme}://{username}:{password}@{server}:{port}'.format(**proxy)
    elif proxy.get('username') and proxy.get('server') and proxy.get('port'):
        proxy_address = '{scheme}://{username}@{server}:{port}'.format(**proxy)
    elif proxy.get('server') and proxy.get('port'):
        proxy_address = '{scheme}://{server}:{port}'.format(**proxy)
    elif proxy.get('server'):
        proxy_address = '{scheme}://{server}'.format(**proxy)
    else:
        return None

    return dict(http=proxy_address, https=proxy_address)


def get_cond_visibility(condition):
    """Test a condition in XBMC"""
    return xbmc.getCondVisibility(condition)


def has_inputstream_adaptive():
    """Whether InputStream Adaptive is installed and enabled in add-on settings"""
    return get_setting_bool('useinputstreamadaptive', default=True) and has_addon('inputstream.adaptive')


def has_addon(name):
    """Checks if add-on is installed"""
    return xbmc.getCondVisibility('System.HasAddon(%s)' % name) == 1


def has_credentials():
    """Whether the add-on has credentials filled in"""
    return bool(get_setting('username') and get_setting('password'))


def kodi_version():
    """Returns major Kodi version"""
    return int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0])


def can_play_drm():
    """Whether this Kodi can do DRM using InputStream Adaptive"""
    return get_setting_bool('usedrm', default=True) and get_setting_bool('useinputstreamadaptive', default=True) and supports_drm()


def supports_drm():
    """Whether this Kodi version supports DRM decryption using InputStream Adaptive"""
    return kodi_version() > 17


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
    log(3, "Create directory '{path}'.", path=path)
    return vfsmkdir(path)


def mkdirs(path):
    """Create directory including parents (using xbmcvfs)"""
    from xbmcvfs import mkdirs as vfsmkdirs
    log(3, "Recursively create directory '{path}'.", path=path)
    return vfsmkdirs(path)


def exists(path):
    """Whether the path exists (using xbmcvfs)"""
    from xbmcvfs import exists as vfsexists
    return vfsexists(path)


# @contextmanager
# def open_file(path, flags='r'):
#     """Open a file (using xbmcvfs)"""
#     from xbmcvfs import File
#     fdesc = File(path, flags)
#     yield fdesc
#     fdesc.close()
#

def stat_file(path):
    """Return information about a file (using xbmcvfs)"""
    from xbmcvfs import Stat
    return Stat(path)


def delete(path):
    """Remove a file (using xbmcvfs)"""
    from xbmcvfs import delete as vfsdelete
    log(3, "Delete file '{path}'.", path=path)
    return vfsdelete(path)


def delete_cached_thumbnail(url):
    """Remove a cached thumbnail from Kodi in an attempt to get a realtime live screenshot"""
    # Get texture
    result = jsonrpc(method='Textures.GetTextures', params=dict(
        filter=dict(
            field='url',
            operator='is',
            value=url,
        ),
    ))
    if result.get('result', {}).get('textures') is None:
        log_error('URL {url} not found in texture cache', url=url)
        return False

    texture_id = next((texture.get('textureid') for texture in result.get('result').get('textures')), None)
    if not texture_id:
        log_error('URL {url} not found in texture cache', url=url)
        return False
    log(2, 'found texture_id {id} for url {url} in texture cache', id=texture_id, url=url)

    # Remove texture
    result = jsonrpc(method='Textures.RemoveTexture', params=dict(textureid=texture_id))
    if result.get('result') != 'OK':
        log_error('failed to remove {url} from texture cache: {error}', url=url, error=result.get('error', {}).get('message'))
        return False

    log(2, 'succesfully removed {url} from texture cache', url=url)
    return True


def input_down():
    """Move the cursor down"""
    jsonrpc(method='Input.Down')


def current_container_url():
    """Get current container plugin:// url"""
    url = xbmc.getInfoLabel('Container.FolderPath')
    if url == '':
        return None
    return url


def container_refresh(url=None):
    """Refresh the current container or (re)load a container by URL"""
    if url:
        log(3, 'Execute: Container.Refresh({url})', url=url)
        xbmc.executebuiltin('Container.Refresh({url})'.format(url=url))
    else:
        log(3, 'Execute: Container.Refresh')
        xbmc.executebuiltin('Container.Refresh')


def container_update(url):
    """Update the current container while respecting the path history."""
    if url:
        log(3, 'Execute: Container.Update({url})', url=url)
        xbmc.executebuiltin('Container.Update({url})'.format(url=url))
    else:
        # URL is a mandatory argument for Container.Update, use Container.Refresh instead
        container_refresh()


def container_reload(url=None):
    """Only update container if the play action was initiated from it"""
    if url is None:
        url = get_property('container.url')
    if current_container_url() != url:
        return
    container_update(url)


def end_of_directory():
    """Close a virtual directory, required to avoid a waiting Kodi"""
    from resources.lib.addon import routing
    xbmcplugin.endOfDirectory(handle=routing.handle, succeeded=False, updateListing=False, cacheToDisc=False)


def log(level=1, message='', **kwargs):
    """Log info messages to Kodi"""
    debug_logging = get_global_setting('debug.showloginfo')  # Returns a boolean
    max_log_level = get_setting_int('max_log_level', default=0)
    if not debug_logging and not (level <= max_log_level and max_log_level != 0):
        return
    if kwargs:
        from string import Formatter
        message = Formatter().vformat(message, (), SafeDict(**kwargs))
    message = '[{addon}] {message}'.format(addon=addon_id(), message=message)
    xbmc.log(from_unicode(message), level % 3 if debug_logging else 2)


def log_access(url, query_string=None):
    """Log addon access"""
    message = 'Access: %s' % (url + ('?' + query_string if query_string else ''))
    log(1, message)


def log_error(message, **kwargs):
    """Log error messages to Kodi"""
    if kwargs:
        from string import Formatter
        message = Formatter().vformat(message, (), SafeDict(**kwargs))
    message = '[{addon}] {message}'.format(addon=addon_id(), message=message)
    xbmc.log(from_unicode(message), 4)


def jsonrpc(*args, **kwargs):
    """Perform JSONRPC calls"""
    from json import dumps, loads

    # We do not accept both args and kwargs
    if args and kwargs:
        log_error('Wrong use of jsonrpc()')
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
