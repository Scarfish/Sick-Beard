# -*- coding: utf-8 -*-
__title__ = 'subliminal'
__version__ = '0.8.0'
__author__ = 'Antoine Bertin'
__license__ = 'MIT'
__copyright__ = 'Copyright 2013 Antoine Bertin'

import os.path
import pkg_resources
import logging

MY_PATH = os.path.dirname(os.path.normpath(__file__))

distrib = pkg_resources.Distribution(location=os.path.dirname(MY_PATH), project_name='SubliminaL4SickbearD', version='0.0.1')
entry_point = { 'babelfish.language_converters': [  'alpha2 = babelfish.converters.alpha2:Alpha2Converter',
                                                    'alpha3b = babelfish.converters.alpha3b:Alpha3BConverter',
                                                    'alpha3t = babelfish.converters.alpha3t:Alpha3TConverter',
                                                    'name = babelfish.converters.name:NameConverter',
                                                    'scope = babelfish.converters.scope:ScopeConverter',
                                                    'type = babelfish.converters.type:LanguageTypeConverter',
                                                    'opensubtitles = babelfish.converters.opensubtitles:OpenSubtitlesConverter',
                                                    'podnapisi = subliminal.converters.podnapisi:PodnapisiConverter',
                                                    'addic7ed = subliminal.converters.addic7ed:Addic7edConverter',
                                                    'tvsubtitles = subliminal.converters.tvsubtitles:TVsubtitlesConverter'],
                
                'babelfish.country_converters': ['name = babelfish.converters.countryname:CountryNameConverter'],
                
                'subliminal.providers': ['thesubdb = subliminal.providers.thesubdb:TheSubDBProvider',
                                         'opensubtitles = subliminal.providers.opensubtitles:OpenSubtitlesProvider',
                                         'addic7ed = subliminal.providers.addic7ed:Addic7edProvider',
                                         'podnapisi = subliminal.providers.podnapisi:PodnapisiProvider',
                                         'tvsubtitles = subliminal.providers.tvsubtitles:TVsubtitlesProvider'],
                }

distrib._ep_map = pkg_resources.EntryPoint.parse_map(entry_point, distrib)
pkg_resources.working_set.add(distrib)

from .api import list_subtitles, download_subtitles, download_best_subtitles, save_subtitles
from .cache import MutexLock, region as cache_region
from .exceptions import Error, ProviderError, ProviderConfigurationError, ProviderNotAvailable, InvalidSubtitle
from .providers import PROVIDERS, Provider, get_provider, ProviderManager
from .subtitle import Subtitle
from .video import VIDEO_EXTENSIONS, SUBTITLE_EXTENSIONS, Video, Episode, Movie, scan_videos, scan_video

logging.getLogger("subliminal").addHandler(logging.NullHandler())

try:
    cache_region.configure('dogpile.cache.memory')
except:
    logger.log("Error occurred on subliminal cache configuration: " + traceback.format_exc(), logger.ERROR)
