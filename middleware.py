import sys, traceback
import urllib2
import yaml
from django.views.debug import get_safe_settings
from django.conf import settings

class HoptoadNotifierMiddleware(object):
    def __init__(self):
        super(HoptoadNotifierMiddleware, self).__init__()
    
    def process_exception(self, request, exc):
        print 'Processing!'
        excc, _, trace = sys.exc_info()
        
        message = str(exc)
        trace = [line.strip() for line in traceback.format_tb(trace)]
        environment = dict( (k, str(v)) for (k, v) in get_safe_settings().items() )
        request_get = dict( (k, str(v)) for (k, v) in request.GET.items() )
        
        headers = { 'Content-Type': 'application/x-yaml', 
                    'Accept': 'text/xml, application/xml', }
        data = yaml.dump({ 'notice': {
                'api_key':       settings.HOPTOAD_API_KEY,
                'error_class':   excc.__name__,
                'error_message': "%s: %s" % (excc.__name__, message),
                'backtrace':     trace,
                'request':       { 'url': request.build_absolute_uri(),
                                   'params': request_get },
                'session':       {},
                'environment':   environment,
            }
        })
        r = urllib2.Request('http://hoptoadapp.com/notices', data, headers)
        print '\n'.join(l for l in urllib2.urlopen(r))
        
        return None
    
