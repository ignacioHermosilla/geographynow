from django.shortcuts import render
import json
import collections
import arrow
from .models import Country


def get_countries_info():
    data = collections.OrderedDict()
    for country in Country.objects.all().order_by('name'):
        data[country.code] = {
            'youtube': country.geo_video_url,
            'name': country.name,
            'flag_friday_video_url': country.flag_friday_video_url
        }
    return data


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
