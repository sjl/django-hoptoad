import sys, traceback
import urllib2
import yaml
from django.core.exceptions import MiddlewareNotUsed
from django.views.debug import get_safe_settings
from django.conf import settings

def _parse_environment():
    return dict( (str(k), str(v)) for (k, v) in get_safe_settings().items() )

def _parse_traceback(tb):
    tb = [ "%s:%d:in `%s'" % (filename, lineno, funcname) 
                  for filename, lineno, funcname, _
                  in traceback.extract_tb(tb) ]
    tb.reverse()
    return tb

def _parse_message(exc, exc_class):
    return '%s: %s' % (exc_class.__name__, str(exc))

def _parse_request(request):
    request_get = dict( (str(k), str(v)) for (k, v) in request.GET.items() )
    request_post = dict( (str(k), str(v)) for (k, v) in request.POST.items() )
    return request_post if request_post else request_get

def _parse_session(session):
    return dict( (str(k), str(v)) for (k, v) in session.items() )


def _generate_payload(exc, excc, tb, request):
    message = _parse_message(exc, excc)
    traceback = _parse_traceback(tb)
    environment = _parse_environment()
    req = _parse_request(request)
    session = _parse_session(request.session)
    
    return yaml.dump({ 'notice': {
        'api_key':       settings.HOPTOAD_API_KEY,
        'error_class':   excc.__name__,
        'error_message': message,
        'backtrace':     traceback,
        'request':       { 'url': request.build_absolute_uri(),
                           'params': req },
        'session':       { 'key': '', 'data': session },
        'environment':   environment,
    }}, default_flow_style=False)


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
        
        headers = { 'Content-Type': 'application/x-yaml', 
                    'Accept': 'text/xml, application/xml', }
        data = _generate_payload(exc, excc, tb, request)
                
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
    
