from django.conf.urls import url, include
from . import views


scheme_urls = [
    url(r'^(?P<scheme_pid>[0-9]+)/$', views.view_scheme, name='viewscheme'),
    url(r'^setting/(?P<scheme_pid>[0-9]+)/$', views.view_scheme_settings, name='viewschemesetting'),
    url(r'^setting/(?P<scheme_pid>[0-9]+)/save$', views.save_scheme_settings, name='saveschemesetting'),
    url(r'^create/$', views.create_scheme, name='create_scheme'),
]


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.user_register, name='userregister'),
    url(r'^login/$', views.user_login, name='userlogin'),
    url(r'^logout/$', views.user_logout, name='userlogout'),
    url(r'^services/$', views.view_services, name='viewservices'),
    url(r'^fusion/$', views.service_fusion, name='servicefusion'),
    url(r'^fusion/scheme/', include(scheme_urls)),
    url(r'^fission/$', views.service_fission, name='servicefission')
]