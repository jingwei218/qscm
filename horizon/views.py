from django.shortcuts import render
from django.contrib.auth.models import User
from horizon.models import Setting


def index(request):
    setting = Setting.objects.all()
    return render(request, 'horizon.html',
                  {
                      'lang': 'en',
                      'title': 'test',
                      'setting': setting,
                   })
