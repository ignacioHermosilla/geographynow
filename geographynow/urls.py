from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import webmap.views

urlpatterns = [
    url(r'', webmap.views.index, name='index'),
]