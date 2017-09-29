from django.conf.urls import url, include
from demo7 import views

urlpatterns = [
    url(r'^$', views.frontpage, name='index2'),
]