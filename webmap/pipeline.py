from apiclient.discovery import build
import pycountry
import difflib
import arrow
import json
import re
import os
from django.conf import settings
from .models import Country
from webpush.models import SubscriptionInfo
from .utils import send_slack_log, send_push_notification

BLACK_LIST = ['Bandiaterra', 'DOMINICAN REPUBLIC (Flag Friday)']

# @@TODO: case insensitive
MANUAL_MAPPING = {
    'czech republic (czechia)': 'CZ',
    'congo (republic)': 'CG',
    'congo (democratic republic)': 'CD',
    'cape verde': 'CV',
    'brunei': 'BN',
    'bolivia': 'BO',
    'the bahamas': 'BS',
    'east timor': 'TL',
    'the gambia': 'GM',
    'rep. of macedonia (f.y.r.o.m)': 'MK',
}

GEO_VIDEO_PATTERN = r'\(?[Gg]eography [Nn]ow!?\)?'
FLAG_FRIDAY_PATTERN = r'\(?[Ff]lag [Ff]riday!?\)?'


def _clean_title(title):
    title = re.sub(GEO_VIDEO_PATTERN, '', title)
    title = re.sub(FLAG_FRIDAY_PATTERN, '', title)
    title = title.replace('!', '')
    return title.strip()


def get_best_match(title):
    original_title = title
    title = _clean_title(title)
    max_ratio = 0.0
    selected_country = None
    for country in pycountry.countries:
        seq = difflib.SequenceMatcher(a=country.name.lower(), b=title.strip().lower())
        ratio = seq.ratio()
        if ratio > 0.90 and ratio > max_ratio:
            max_ratio = ratio
            selected_country = country

    if selected_country:
        return selected_country

    if MANUAL_MAPPING.get(title.lower()):
        return pycountry.countries.get(alpha_2=MANUAL_MAPPING.get(title.lower()))
    elif title in BLACK_LIST:
        return None
    else:
        # send slack message
        send_slack_log("[Geo now] no country", title + ' | ' + original_title)
        return None


def get_playlist_info(playlist, video_field_name):
    developer_key = os.getenv('YOUTUBE_DEVELOPER_KEY')
    if not developer_key and hasattr(settings, 'YOUTUBE_DEVELOPER_KEY') and settings.YOUTUBE_DEVELOPER_KEY:
        developer_key = settings.YOUTUBE_DEVELOPER_KEY

    if not developer_key:
        print "youtube developer key undefined, skip"
        return

    youtube = build(
        settings.YOUTUBE_API_SERVICE_NAME,
        settings.YOUTUBE_API_VERSION,
        developerKey=developer_key
    )
    search_request = youtube.playlistItems().list(
        playlistId=playlist,
        maxResults=50,
        part="id,snippet,contentDetails",
    )
    index_country = {}
    while search_request:
        search_response = search_request.execute()
        for video_info in search_response['items']:
            title = video_info['snippet']['title']
            video_id = video_info['snippet']['resourceId']['videoId']
            video_url = 'https://www.youtube.com/embed/{}'.format(video_id)
            country = get_best_match(title)
            if country:
                index_country[country.name] = country.alpha_2
                # create or update
                defaults = {
                    'name': country.name,
                    video_field_name: video_url,
                    'updated_at': arrow.utcnow().datetime
                }
                country, created = Country.objects.update_or_create(
                    code=country.alpha_2,
                    defaults=defaults
                )
                if created:
                    # internal notification
                    send_slack_log("[Geo now] new country", country.name)
                    # notify to subscribed users (web push)
                    # @@TODO: move this from here to an async task
                    if settings.WEBPUSH_ENABLED:
                        if video_field_name == 'geo_video_url':
                            body = 'New country video'
                        else:
                            body = 'New flag friday video'

                        payload = {
                            "head": country.name,
                            "body": body,
                            "icon": country.flag_icon,
                        }
                        json_payload = json.dumps(payload)
                        for subscription in SubscriptionInfo.objects.all():
                            send_push_notification(subscription, json_payload, ttl=7000)

        search_request = youtube.playlistItems().list_next(
            search_request,
            search_response
        )


def update_country_info():
    get_playlist_info(
        playlist=settings.GEO_PLAYLIST,
        video_field_name='geo_video_url'
    )
    get_playlist_info(
        playlist=settings.FLAG_FRIDAY_PLAYLIST,
        video_field_name='flag_friday_video_url'
    )
