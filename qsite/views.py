from django.shortcuts import render
from qsite.models import NavigationBar


def index(request):
    nav = NavigationBar.objects.all()
    return render(request, 'qsite/login.html',
                  {'lang': 'ch',
                   'title': 'Quantum',
                   'nav': nav,
                   })