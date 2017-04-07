import requests
from django.conf import settings
from django.forms.models import model_to_dict
import os

from pywebpush import WebPusher


def send_slack_log(title, message):
    slack_url = os.getenv('SLACK_URL')
    if not slack_url and hasattr(settings, 'SLACK_URL') and settings.SLACK_URL:
        slack_url = settings.SLACK_URL

    if slack_url:
        payload = {"text": message, "username": title}
        requests.post(slack_url, json=payload)


def send_push_notification(subscription, payload, ttl):
    subscription_data = _process_subscription_info(subscription)
    # Check if GCM info is provided in the settings
    gcm_key = os.getenv('GCM_KEY')
    if not gcm_key and settings.GCM_KEY:
        gcm_key = settings.WEBPUSH_SETTINGS.get('GCM_KEY')

    req = WebPusher(subscription_data).send(data=payload, ttl=ttl, gcm_key=gcm_key)
    return req


def _process_subscription_info(subscription):
    subscription_data = model_to_dict(subscription, exclude=["browser", "id"])
    endpoint = subscription_data.pop("endpoint")
    p256dh = subscription_data.pop("p256dh")
    auth = subscription_data.pop("auth")

    return {
        "endpoint": endpoint,
        "keys": {"p256dh": p256dh, "auth": auth}
    }
