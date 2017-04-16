from django.conf.urls import url, include
from . import views


scheme_urls = [
    url(r'^(?P<scheme_pid>[0-9]+)/$', views.viewScheme, name='viewscheme'),
    url(r'^setting/(?P<scheme_pid>[0-9]+)/$', views.viewSchemeSetting, name='viewschemesetting'),
    url(r'^setting/(?P<scheme_pid>[0-9]+)/save$', views.saveSchemeSetting, name='viewschemesetting'),
]


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.userRegister, name='userregister'),
    url(r'^login/$', views.userLogin, name='userlogin'),
    url(r'^logout/$', views.userLogout, name='userlogout'),
    url(r'^services/$', views.services, name='services'),
    url(r'^dawn/$', views.dawn, name='dawn'),
    url(r'^dawn/scheme/new/$', views.newScheme, name='newscheme'),
    url(r'^dawn/scheme/', include(scheme_urls)),
]