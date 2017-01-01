from django.shortcuts import render
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from horizon.models import Setting, DataElement


def index(request):
    settings = Setting.objects.all()
    data_elements = DataElement.objects.all()
    return render(request, 'horizon.html',
                  {
                      'lang': 'en',
                      'title': 'test',
                      'settings': settings,
                      'data_elements': data_elements,
                   })


def result(request):
    return TemplateResponse(request, 'result.html', {
        'result': request.POST
    })