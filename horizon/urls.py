from django.conf.urls import url, include
from . import views


scheme_urls = [
    url(r'^get/(?P<scheme_hash_pid>\w+)/$', views.get_datasheets, name='get_datasheets'),
    url(r'^settings/$', views.get_scheme_settings, name='view_scheme_settings'),
    url(r'^settings/save/$', views.save_scheme_settings, name='save_scheme_settings'),
    url(r'^settings/lock/$', views.lock_scheme_settings, name='lock_scheme_settings'),
]

datasheet_urls = [
    url(r'^settings/$', views.get_datasheet_settings, name='view_datasheet_settings'),
    url(r'^settings/save/$', views.save_datasheet_settings, name='save_datasheet_settings'),
    url(r'^settings/lock/$', views.lock_datasheet_settings, name='lock_datasheet_settings'),
    url(r'^fields/save/$', views.save_datasheet_fields, name='save_datasheet_fields'),
    url(r'^template/download/(?P<datasheet_hash_pid>\w+)/$', views.get_datasheet_template, name='get_datasheet_template'),
    url(r'^upload/$', views.upload_datasheet_file, name='upload_datasheet_file'),
]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.user_register, name='userregister'),
    url(r'^login/$', views.user_login, name='userlogin'),
    url(r'^logout/$', views.user_logout, name='userlogout'),
    url(r'^services/$', views.view_services, name='viewservices'),
    url(r'^fusion/$', views.service_fusion, name='servicefusion'),
    url(r'^fusion/scheme/', include(scheme_urls)),
    url(r'^fusion/datasheet/', include(datasheet_urls)),
    url(r'^fission/$', views.service_fission, name='servicefission')
]