import sys
import traceback
import urllib2
import yaml
from xml.dom.minidom import getDOMImplementation

from django.views.debug import get_safe_settings
from django.conf import settings

from hoptoad import VERSION, NAME, URL
from hoptoad import get_hoptoad_settings
from hoptoad.api.htv1 import _parse_environment, _parse_request, _parse_session
from hoptoad.api.htv1 import _parse_message


def _class_name(class_):
    return class_.__class__.__name__

def _handle_errors(request, response, exc):
    if response:
        code = "Http%s" % response
        msg = "%(code)s: %(response)s at %(uri)s" % {
                   'code': code,
                   'response': { 'Http403': "Forbidden",
                                 'Http404': "Page not found" }[code],
                   'uri': request.build_absolute_uri()
        }
        return (code, msg)
    
    excc, inst = sys.exc_info()[:2]
    if exc:
        excc = exc
    return _class_name(excc), _parse_message(excc)


def generate_payload(request, response=None, exc=None):
    """Generate an XML payload for a Hoptoad notification.
    
    Parameters:
    request -- A Django HTTPRequest.
    
    """
    hoptoad_settings = get_hoptoad_settings()
    p_error_class, p_message = _handle_errors(request, response, exc)
    
    # api v2 from: http://help.hoptoadapp.com/faqs/api-2/notifier-api-v2
    xdoc = getDOMImplementation().createDocument(None, "notice", None)
    notice = xdoc.firstChild
    
    # /notice/@version -- should be 2.0
    notice.setAttribute('version', '2.0')
    
    # /notice/api-key
    api_key = xdoc.createElement('api-key')
    api_key_data = xdoc.createTextNode(hoptoad_settings['HOPTOAD_API_KEY'])
    api_key.appendChild(api_key_data)
    notice.appendChild(api_key)
    
    # /notice/notifier/name
    # /notice/notifier/version
    # /notice/notifier/url
    notifier = xdoc.createElement('notifier')
    for key, value in zip(["name", "version", "url"], [NAME, VERSION, URL]):
        key = xdoc.createElement(key)
        value = xdoc.createTextNode(str(value))
        key.appendChild(value)
        notifier.appendChild(key)
    notice.appendChild(notifier)
    
    # /notice/error/class
    # /notice/error/message
    error = xdoc.createElement('error')
    for key, value in zip(["class", "message"], [p_error_class, p_message]):
        key = xdoc.createElement(key)
        value = xdoc.createTextNode(value)
        key.appendChild(value)
        error.appendChild(key)
    
    # /notice/error/backtrace/error/line
    backtrace = xdoc.createElement('backtrace')
    # i do this here because I'm afraid of circular reference..
    reversed_backtrace = reversed(traceback.extract_tb(sys.exc_info()[2]))
    for filename, lineno, funcname, text in reversed_backtrace:
        line = xdoc.createElement('line')
        line.setAttribute('file', str(filename))
        line.setAttribute('number', str(lineno))
        line.setAttribute('method', str(funcname))
        backtrace.appendChild(line)
    error.appendChild(backtrace)
    notice.appendChild(error)
    
    # /notice/request
    xrequest = xdoc.createElement('request')
    
    # /notice/request/url -- request.build_absolute_uri()
    xurl = xdoc.createElement('url')
    xurl_data = xdoc.createTextNode(request.build_absolute_uri())
    xurl.appendChild(xurl_data)
    xrequest.appendChild(xurl)
    
    # /notice/request/component -- not sure..
    comp = xdoc.createElement('component')
    #comp_data = xdoc.createTextNode('')
    xrequest.appendChild(comp)
    
    # /notice/request/action -- action which error occured
    # ... no fucking clue..
    
    # sjl: "actions" are the Rails equivalent of Django's views
    #      Is there a way to figure out which view a request object went to
    #      (if any)?  Anyway, it's not GET/POST so I'm commenting it for now.
    
    #action = xdoc.createElement('action') # maybe GET/POST??
    #action_data = u"%s %s" % (request.method, request.META['PATH_INFO'])
    #action_data = xdoc.createTextNode(action_data)
    #action.appendChild(action_data)
    #xrequest.appendChild(action)
    
    # /notice/request/params/var -- check request.GET/request.POST
    params = xdoc.createElement('params')
    for key, value in _parse_request(request).iteritems():
        var = xdoc.createElement('var')
        var.setAttribute('key', key)
        value = xdoc.createTextNode(str(value))
        var.appendChild(value)
        params.appendChild(var)
    xrequest.appendChild(params)
    
    # /notice/request/session/var -- check if sessions is enabled..
    sessions = xdoc.createElement('session')
    for key, value in _parse_session(request.session).iteritems():
        var = xdoc.createElement('var')
        var.setAttribute('key', key)
        value = xdoc.createTextNode(str(value))
        var.appendChild(value)
        sessions.appendChild(var)
    xrequest.appendChild(params)
    
    # /notice/request/cgi-data/var -- all meta data
    cgidata = xdoc.createElement('cgi-data')
    for key, value in _parse_environment(request).iteritems():
        var = xdoc.createElement('var')
        var.setAttribute('key', key)
        value = xdoc.createTextNode(str(value))
        var.appendChild(value)
        cgidata.appendChild(var)
    xrequest.appendChild(cgidata)
    notice.appendChild(xrequest)
    
    # /notice/server-environment
    serverenv = xdoc.createElement('server-environment')
    
    # /notice/server-environment/project-root -- default to sys.path[0] 
    projectroot = xdoc.createElement('project-root')
    projectroot.appendChild(xdoc.createTextNode(sys.path[0]))
    serverenv.appendChild(projectroot)
    
    # /notice/server-environment/environment-name -- environment name? wtf..
    #envname = xdoc.createElement('environment-name')
    # no idea...
    
    # sjl: This is supposed to be set to something like "test", "staging",
    #      or "production" to help you group the errors in the web interface.
    #      I'm still thinking about the best way to support this.
    
    # envname.appendChild(xdoc.createTextNode())
    #serverenv.appendChild(envname)
    notice.appendChild(serverenv)
    
    return xdoc.toxml('utf-8')

def _ride_the_toad(payload, timeout, use_ssl):
    """Send a notification (an HTTP POST request) to Hoptoad.
    
    Parameters:
    payload -- the XML payload for the request from _generate_payload()
    timeout -- the maximum timeout, in seconds, or None to use the default
    
    """
    headers = { 'Content-Type': 'text/xml' }
    
    url_template = '%s://hoptoadapp.com/notifier_api/v2/notices'
    notification_url = url_template % ("https" if use_ssl else "http")
    
    # allow the settings to override all urls
    notification_url = get_hoptoad_settings().get('HOPTOAD_NOTIFICATION_URL',
                                                   notification_url)
    
    r = urllib2.Request(notification_url, payload, headers)
    try:
        if timeout:
            # timeout is 2.6 addition!
            response = urllib2.urlopen(r, timeout=timeout)
        else:
            response = urllib2.urlopen(r)
    except urllib2.URLError:
        pass
    else:
        # getcode is 2.6 addition!
        status = response.getcode()
        
        if status == 403 and use_ssl:
            # if we can not use SSL, re-invoke w/o using SSL
            _ride_the_toad(payload, timeout, use_ssl=False)
        if status == 403 and not use_ssl:
            # we were not trying to use SSL but got a 403 anyway
            # something else must be wrong (bad API key?)
            pass
        if status == 422:
            # couldn't send to hoptoad..
            pass
        if status == 500:
            # hoptoad is down
            pass

def report(payload, timeout):
    use_ssl = get_hoptoad_settings().get('HOPTOAD_USE_SSL', False)
    return _ride_the_toad(payload, timeout, use_ssl)
