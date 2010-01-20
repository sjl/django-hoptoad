"""Implementations of different handlers that communicate with hoptoad in
various different protocols.
"""
import logging
import os
import imp
import pprint

from hoptoad import get_hoptoad_settings
from hoptoad.handlers.threaded import ThreadedNotifier
from hoptoad.handlers.blocking import BlockingNotifier

logger = logging.getLogger(__name__)


def get_handler(*args, **kwargs):
    """Returns an initialized handler object"""
    hoptoad_settings = get_hoptoad_settings()
    handler = hoptoad_settings.get("HOPTOAD_HANDLER", "threadpool")
    if handler.lower() == 'threadpool':
        threads = hoptoad_settings.get("HOPTOAD_THREAD_COUNT", 4)
        return ThreadedNotifier(threads , *args, **kwargs)
    elif handler.lower() == 'blocking':
        return BlockingNotifier(*args, **kwargs)
    else:
        _class_module = hoptoad_settings.get('HOPTOAD_HANDLER_CLASS', None)
        if not _class_module:
            # not defined, abort setting up hoptoad, skip it.
            raise MiddlewareNotUsed
        # module name that we should import from
        _module_name = os.path.splitext(os.path.basename(handler))[0]
        # load the module!
        m = imp.load_module(_module_name,
                            *imp.find_module(_module_name,
                                             [os.path.dirname(handler)]))

        # instantiate the class
        return getattr(m, _class_module)(*args, **kwargs)
