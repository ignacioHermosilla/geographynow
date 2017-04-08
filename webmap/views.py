from django.shortcuts import render
import json
import collections
import arrow
from django.http import HttpResponse
from django.conf import settings
from .models import Country
from django.forms.models import model_to_dict

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from webpush.forms import WebPushForm, SubscriptionForm


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
            'flag_friday_video_url': country.flag_friday_video_url
        }
    return data


"""
Views
"""


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


def ssl_validation(request):
    return HttpResponse('mNZkbVd5oHqE0ntSszAnGdNWMM4IlhaWhQ531RnPYn0.ym40afnU_Hv1HO8gncd2acXeeMyBJrIECmfopGGZc08')


def index(request):
    data = get_countries_info()
    existing_countries = map(str, data.keys())
    # @@TODO: handle empty database
    updated_at = arrow.get(Country.objects.all()[0].updated_at).humanize()
    last_video = Country.get_latest_video_info()
    updated_info_template = '{updated_at} (latest added: {country} {video_type})'
    updated_info = updated_info_template.format(
        updated_at=updated_at,
        country=last_video['country'],
        video_type=last_video['video_type'],
    )

    context = {
        'data': json.dumps(data),
        'areas': existing_countries,
        'updated_at': updated_info,
        'message': 'of geography now!',
    }
    return render(request, 'index.html', context=context)
