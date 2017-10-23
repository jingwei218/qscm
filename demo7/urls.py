from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'multiupload/$', views.multiupload, name='multiupload'),
    url(r'qrcode/$', views.qrcgen, name='qrcgen'),
    url(r'wspush/$', views.wspush, name='wspush'),
    url(r'savetemplate/$', views.savetemplate, name='savetemplate'),
]
