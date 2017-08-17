import webmap.views

from django.conf.urls import include, url
from django.contrib.sitemaps.views import sitemap
from django.contrib import admin
admin.autodiscover()

sitemaps = {
    'site': webmap.views.CountrySitemap,
}

urlpatterns = [
    url(r'^$', webmap.views.index, name='index'),
    url(r'^(?P<country_name>[\w\-]+)/$', webmap.views.country_index, name='country_index'),
    url(
        r'^subscribe_or_unsubscribe_notification',
        webmap.views.subscribe_or_unsubscribe_notification,
        name='subscribe_or_unsubscribe_notification'
    ),

    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^webpush/', include('webpush.urls'))
]
