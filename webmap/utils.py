import requests
from django.conf import settings
import os


def send_slack_log(title, message):
    slack_url = os.getenv('SLACK_URL')
    if not slack_url and hasattr(settings, 'SLACK_URL') and settings.SLACK_URL:
        slack_url = settings.SLACK_URL

    if slack_url:
        payload = {"text": message, "username": title}
        requests.post(slack_url, json=payload)
