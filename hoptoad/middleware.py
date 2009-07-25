import sys, traceback
import urllib2
import yaml
from django.core.exceptions import MiddlewareNotUsed
from django.views.debug import get_safe_settings
from django.conf import settings

class HoptoadNotifierMiddleware(object):
    def __init__(self):
        all_settings = settings.get_all_members()
        if 'HOPTOAD_API_KEY' not in all_settings:
            raise MiddlewareNotUsed
        if settings.DEBUG and (
            not 'HOPTOAD_NOTIFY_WHILE_DEBUG' in all_settings
            or not settings.HOPTOAD_NOTIFY_WHILE_DEBUG ):
            raise MiddlewareNotUsed
        if 'HOPTOAD_TIMEOUT' not in all_settings:
            self.timeout = None
        else:
            self.timeout = settings.HOPTOAD_TIMEOUT
    
    def process_exception(self, request, exc):
        excc, _, tb = sys.exc_info()
        
        message = '%s: %s' % (excc.__name__, str(exc))
        trace = [ "%s:%d:in `%s'" % (filename, lineno, funcname) 
                  for filename, lineno, funcname, _
                  in traceback.extract_tb(tb) ]
        trace.reverse()
        environment = dict( (str(k), str(v)) for (k, v) in get_safe_settings().items() )
        request_get = dict( (str(k), str(v)) for (k, v) in request.GET.items() )
        request_post = dict( (str(k), str(v)) for (k, v) in request.POST.items() )
        session = dict( (str(k), str(v)) for (k, v) in request.session.items() )
        
        headers = { 'Content-Type': 'application/x-yaml', 
                    'Accept': 'text/xml, application/xml', }
        data = yaml.dump({ 'notice': {
            'api_key':       settings.HOPTOAD_API_KEY,
            'error_class':   excc.__name__,
            'error_message': "%s: %s" % (excc.__name__, message),
            'backtrace':     trace,
            'request':       { 'url': request.build_absolute_uri(),
                               'params': request_post if request_post else request_get },
            'session':       { 'key': '', 'data': session },
            'environment':   environment,
        }}, default_flow_style=False)
                
        r = urllib2.Request('http://hoptoadapp.com/notices', data, headers)
        if not self.timeout:
            try:
                urllib2.urlopen(r)
            except urllib2.URLError:
                pass
        else:
            try:
                urllib2.urlopen(r, timeout=self.timeout)
            except urllib2.URLError:
                pass
        
        return None
    
