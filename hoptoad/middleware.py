import sys, traceback
import urllib2
import yaml
from django.core.exceptions import MiddlewareNotUsed
from django.views.debug import get_safe_settings
from django.conf import settings

def _parse_environment(req):
    env = dict( (str(k), str(v)) for (k, v) in get_safe_settings().items() )
    env.update(dict( (str(k), str(v)) for (k, v) in req.META.items() ))
    env['REQUEST_URI'] = req.build_absolute_uri()
    return env

def _parse_traceback(tb):
    tb = [ "%s:%d:in `%s'" % (filename, lineno, funcname) 
                  for filename, lineno, funcname, _
                  in traceback.extract_tb(tb) ]
    tb.reverse()
    return tb

def _parse_message(exc, exc_class):
    return '%s: %s' % (exc_class.__name__, str(exc))

def _parse_request(req):
    request_get = dict( (str(k), str(v)) for (k, v) in req.GET.items() )
    request_post = dict( (str(k), str(v)) for (k, v) in req.POST.items() )
    return request_post if request_post else request_get

def _parse_session(session):
    return dict( (str(k), str(v)) for (k, v) in session.items() )


def _generate_payload(req, exc=None, excc=None, tb=None, mess=None, err_class=None):
    """Generate a YAML payload for a Hoptoad notification.
    
    Parameters:
    req -- A Django HTTPRequest.  This is required.
    
    Keyword parameters:
    exc -- A Python Exception object.  If this is not given the 
           mess parameter must be.
    excc -- A Python class object representing the exception class.  If
            this is not given the err_class parameter must be.
    tb -- A Python Traceback object.  This is not required.
    mess -- A string representing the error message.  If this is not
            given, the exc parameter must be.
    err_class -- A string representing the error class.  If this is not
                 given the excc parameter must be.
    """
    message = mess if mess else _parse_message(exc, excc)
    error_class = err_class if err_class else excc.__name__
    traceback = _parse_traceback(tb) if tb else []
    environment = _parse_environment(req)
    request = _parse_request(req)
    session = _parse_session(req.session)
    
    return yaml.dump({ 'notice': {
        'api_key':       settings.HOPTOAD_API_KEY,
        'error_class':   error_class,
        'error_message': message,
        'backtrace':     traceback,
        'request':       { 'url': req.build_absolute_uri(),
                           'params': request },
        'session':       { 'key': '', 'data': session },
        'environment':   environment,
    }}, default_flow_style=False)

def _ride_the_toad(payload, timeout):
    """Send a notification (an HTTP POST request) to Hoptoad.
    
    Parameters:
    payload -- the YAML payload for the request from _generate_payload()
    timeout -- the maximum timeout, in seconds, or None to use the default
    """
    headers = { 'Content-Type': 'application/x-yaml', 
                'Accept': 'text/xml, application/xml', }
    r = urllib2.Request('http://hoptoadapp.com/notices', payload, headers)
    try:
        if timeout:
            urllib2.urlopen(r, timeout=timeout)
        else:
            urllib2.urlopen(r)
    except urllib2.URLError:
        pass


class HoptoadNotifierMiddleware(object):
    def __init__(self):
        """Initialize the middleware."""
        all_settings = settings.get_all_members()
        
        if 'HOPTOAD_API_KEY' not in all_settings:
            raise MiddlewareNotUsed
        
        if settings.DEBUG and \
           (not 'HOPTOAD_NOTIFY_WHILE_DEBUG' in all_settings
            or not settings.HOPTOAD_NOTIFY_WHILE_DEBUG ):
            raise MiddlewareNotUsed
        
        self.timeout = ( settings.HOPTOAD_TIMEOUT 
                         if 'HOPTOAD_TIMEOUT' in all_settings else None )
        
        self.notify_404 = ( settings.HOPTOAD_NOTIFY_404 
                            if 'HOPTOAD_NOTIFY_404' in all_settings else False )
    
    def process_response(self, request, response):
        """Process a reponse object.
        
        Hoptoad will be notified of a 404 error if the response is a 404
        and 404 tracking is enabled in the settings.
        
        Regardless of whether Hoptoad is notified, the reponse object will
        be returned unchanged.
        """
        if self.notify_404 and response.status_code == 404:
            error_class = 'Http404'
            
            message = 'Http404: Page not found at %s' % request.build_absolute_uri()
            payload = _generate_payload(request, err_class=error_class, mess=message)
            
            _ride_the_toad(payload, self.timeout)
        
        return response
    
    def process_exception(self, request, exc):
        """Process an exception.
        
        Hoptoad will be notified of the exception and None will be
        returned so that Django's normal exception handling will then
        be used.
        """
        excc, _, tb = sys.exc_info()
        
        payload = _generate_payload(request, exc, excc, tb)
        _ride_the_toad(payload, self.timeout)
        
        return None
    

