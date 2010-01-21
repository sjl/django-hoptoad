import os
import time
import logging

from hoptoad.api import htv2

logger = logging.getLogger(__name__)

class BlockingNotifier(object):
    """A blocking Hoptoad notifier.  """
    def __init__(self):
        _threadname = "Hoptoad%s-%d" % (self.__class__.__name__, os.getpid())

    def enqueue(self, payload, timeout):
        htv2.report(payload, timeout)
