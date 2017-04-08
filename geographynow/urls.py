from django.conf.urls import include, url
import webmap.views
from django.contrib import admin
admin.autodiscover()


urlpatterns = [
    url(r'^$', webmap.views.index, name='index'),
    url(
        r'^subscribe_or_unsubscribe_notification',
        webmap.views.subscribe_or_unsubscribe_notification,
        name='subscribe_or_unsubscribe_notification'
    ),
    url('.well-known/acme-challenge/mNZkbVd5oHqE0ntSszAnGdNWMM4IlhaWhQ531RnPYn0', webmap.views.ssl_validation),
    url(r'^webpush/', include('webpush.urls'))
]
