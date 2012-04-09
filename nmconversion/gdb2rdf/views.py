# Create your views here.

from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
import pgeo2n3
import os

def handlefile(f):
    destination = open('/tmp/input.mdb', 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    pgeo2n3.ConvertMdbToN3('/tmp/input.mdb', '/home/dmattli/code/SemanticNationalMap/nmconversion/gdb2rdf/static/output.n3')

class UploadFileForm(forms.Form):
    file  = forms.FileField()

def index(request):
    if request.method == 'POST':
        a = request.POST
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
                handlefile(request.FILES['file'])
                return HttpResponseRedirect('/static/output.n3')
        else:
                print('Invalid form!')
    else:
        form = UploadFileForm()
        c = {'form': form}
        c.update(csrf(request))
        return render_to_response('gdb2rdf/index.html', c)
