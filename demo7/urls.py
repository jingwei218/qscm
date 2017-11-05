from django.conf.urls import url, include
from demo7 import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'multiupload/$', views.multiupload, name='multiupload'),
    url(r'qrcode/$', views.qrcgen, name='qrcgen'),
    url(r'wspush/$', views.wspush, name='wspush'),
    url(r'addelement/$', views.addelement, name='addelement'),
    url(r'savetemplate/$', views.savetemplate, name='savetemplate'),
    url(r'loadtemplate/$', views.loadtemplate, name='loadtemplate'),
]
