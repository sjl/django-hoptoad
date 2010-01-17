import os
import threading
import time
import logging

from hoptoad.api import htv2

from hoptoad.handlers.utils.threadpool import WorkRequest, ThreadPool
from hoptoad.handlers.utils.threadpool import NoResultsPending


logger = logging.getLogger(__name__)


def _exception_handler(request, exc_info):
    """Rudimentary exception handler, simply log and moves on.

    If there's no tuple, it means something went really wrong. Critically log
    and exit.

    """
    if not isinstance(exc_info, tuple):
        logger.critical(str(request))
        logger.critical(str(exc_info))
        sys.exit(1)
    logger.warn(
        "* Exception occured in request #%s: %s" % (request.requestID, exc_info)
    )


class ThreadedNotifier(threading.Thread):
    """A daemon thread that spawns a threadpool of worker threads.

    Waits for queue additions through the enqueue method.

    """
    def __init__(self, threadpool_threadcount, cb=None, exc_cb=None):
        _threadname = "Hoptoad%s-%d" % (self.__class__.__name__, os.getpid())
        threading.Thread.__init__(self, name=_threadname)
        self.threads = threadpool_threadcount
        self.daemon = True # daemon thread... important!
        self.callback = cb
        self.exc_callback = exc_cb or _exception_handler
        self.pool = ThreadPool(self.threads)
        # start the thread pool
        self.start()

    def enqueue(self, payload, timeout):
        request = WorkRequest(
            htv2.report,
            args=(payload, timeout),
            callback=self.callback,
            exc_callback=self.exc_callback
        )

        # Put the request into the queue where the detached 'run' method will
        # poll its queue every 0.5 seconds and start working.
        self.pool.putRequest(request)

    def run(self):
        """Actively poll the queue for requests and process them."""
        while True:
            try:
                time.sleep(0.5) # TODO: configure for tuning
                self.pool.poll()
            except KeyboardInterrupt:
                logger.info("* Interrupted!")
                break
            except NoResultsPending:
                pass


