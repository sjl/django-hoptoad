"""Implementations of different handlers that communicate with hoptoad in
various different protocols.
"""
import logging

from hoptoad import get_hoptoad_settings
from hoptoad.handlers.threaded import ThreadedNotifier


logger = logging.getLogger(__name__)

def get_handler(*args, **kwargs):
    """Returns an initialized handler object"""
    hoptoad_settings = get_hoptoad_settings()
    handler = hoptoad_settings.get("HOPTOAD_HANDLER", "threadpool")
    if handler.lower() == 'threadpool':
        threads = hoptoad_settings.get("HOPTOAD_THREAD_COUNT", 4)
        return ThreadedNotifier(threads , *args, **kwargs)
