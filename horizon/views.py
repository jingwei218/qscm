from django.shortcuts import render
from horizon.models import BoardSetting


def index(request):
    bsetting = BoardSetting.objects.filter()
    return render(request, 'horizon.html',
                  {
                      'lang': 'en',
                      'title': 'test'
                   })
