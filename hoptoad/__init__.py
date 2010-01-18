from django.conf import settings
from itertools import ifilter


__version__ = 0.3
VERSION = __version__
NAME = "django-hoptoad"
URL = "http://bitbucket.org/sjl/django-hoptoad"


def get_hoptoad_settings():
    hoptoad_settings = getattr(settings, "HOPTOAD_SETTINGS", None)

    if not hoptoad_settings:
        # do some backward compatibility work to combine all hoptoad
        # settings in a dictionary
        hoptoad_settings = {}
        # for every attribute that starts with hoptoad
        for attr in ifilter(lambda x: x.startswith('HOPTOAD'), dir(settings)):
            hoptoad_settings[attr] = getattr(settings, attr)

        if not hoptoad_settings:
            # there were no settings for hoptoad at all..
            # should probably log here
            raise MiddlewareNotUsed

    return hoptoad_settings
