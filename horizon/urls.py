from django.conf.urls import url, include
from . import views


scheme_urls = [
    url(r'^get/(?P<scheme_hash_pid>\w+)/$', views.view_scheme, name='view_scheme'),
    url(r'^save/$', views.save_scheme, name='save_scheme'),
    url(r'^settings/$', views.view_scheme_settings, name='view_scheme_settings'),
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