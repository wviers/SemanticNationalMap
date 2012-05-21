# Create your views here.
from django.http import Http404
from django.template import Context, loader
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
import json
import httplib
from string import Template
import mimetypes
import urllib2


def sparqlproxy(request, path, target_url):
    url = '%s%s' % (target_url, path)
    if request.META.has_key('QUERY_STRING'):
        url += '?' + request.META['QUERY_STRING']
    try:
        print(url)
        proxied_request = urllib2.urlopen(url)
        status_code = proxied_request.code
        mimetype = proxied_request.headers.typeheader or mimetypes.guess_type(url)
        content = proxied_request.read()
    except urllib2.HTTPError as e:
        print('ohno!')
        return HttpResponse(e.msg, status=e.code, mimetype='text/plain')
    else:
        return HttpResponse(content, status=status_code, mimetype=mimetype)

    

def loadindex(request):
    c = RequestContext(request)
    t = loader.get_template('index.html')
    c.update(csrf(request))
    return HttpResponse(t.render(c))

