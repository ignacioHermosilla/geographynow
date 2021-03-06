from django.shortcuts import render
import json
import urllib
import collections
from django.http import HttpResponse
from .models import Country

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from webpush.forms import WebPushForm, SubscriptionForm
from django.contrib.sitemaps import Sitemap


"""
Helpers: @@TODO: move to utils
"""


def process_subscription_data(post_data):
    """Process the subscription data according to out model"""
    subscription_data = post_data.pop("subscription", {})
    # As our database saves the auth and p256dh key in separate field,
    # we need to refactor it and insert the auth and p256dh keys in the same dictionary
    keys = subscription_data.pop("keys", {})
    subscription_data.update(keys)
    # Insert the browser name
    subscription_data["browser"] = post_data.pop("browser")
    return subscription_data


def get_countries_info():
    data = collections.OrderedDict()
    for country in Country.objects.all().order_by('name'):
        data[country.code] = {
            'youtube': country.geo_video_url,
            'name': country.name,
            'flag_friday_video_url': country.geo_video_url  # @TODO: temporary, decide if remove completely flag friday videos
        }
    return data


"""
Views
"""


class CountrySitemap(Sitemap):
    changefreq = "never"
    priority = 0.8

    def items(self):
        return Country.objects.filter()

    def lastmod(self, obj):
        return obj.created_at


@require_POST
@csrf_exempt
def subscribe_or_unsubscribe_notification(request):
    # Parse the  json object from post data. return 400 if the json encoding is wrong
    try:
        post_data = json.loads(request.body)
    except ValueError:
        return HttpResponse(status=400)

    # Process the subscription data to mach with the model
    subscription_data = process_subscription_data(post_data)
    subscription_form = SubscriptionForm(subscription_data)
    # pass the data through WebPushForm for validation purpose
    web_push_form = WebPushForm(post_data)

    # Check if subscriptioninfo and the web push info bot are valid
    if subscription_form.is_valid() and web_push_form.is_valid():
        # Get the cleaned data in order to get status_type
        web_push_data = web_push_form.cleaned_data
        status_type = web_push_data.pop("status_type")

        # Save the subscription info with subscription data
        # as the subscription data is a dictionary and its valid
        subscription = subscription_form.get_or_save(subscription_data)
        if status_type == "unsubscribe":
            subscription.delete()

        # If subscribe is made, means object is created. So return 201
        if status_type == 'subscribe':
            return HttpResponse(status=201)
        # Unsubscribe is made, means object is deleted. So return 202
        elif "unsubscribe":
            return HttpResponse(status=202)

    return HttpResponse(status=400)


def _get_context(initial_country=None):
    data = get_countries_info()
    existing_countries = map(str, data.keys())
    # @@TODO: handle empty database
    last_video = Country.get_latest_video_info()
    updated_info_template = '{updated_at} (latest added: {country} {video_type})'
    updated_info = updated_info_template.format(
        updated_at=last_video['video_added_at_humanized'],
        country=last_video['country'],
        video_type=last_video['video_type'],
    )

    context = {
        'title': 'Geography Now map',
        'description': 'Map with the available geography now videos.',
        'data': json.dumps(data),
        'areas': existing_countries,
        'updated_at': updated_info,
        'message': 'of Geography Now!',
        'initial_country': None
    }
    if initial_country:
        context['title'] = 'Geography Now map {}'.format(initial_country.name)
        context['description'] = '{}. Map with the available geography now videos.'.format(initial_country.name)
        context['initial_country'] = initial_country.code

    return context


def country_index(request, country_name):
    country_name = urllib.unquote(urllib.unquote(country_name))
    try:
        country = Country.objects.get(name=country_name)
        context = _get_context(country)
    except Country.DoesNotExist:
        context = _get_context()
    return render(request, 'index.html', context=context)


def index(request):
    context = _get_context()
    return render(request, 'index.html', context=context)
