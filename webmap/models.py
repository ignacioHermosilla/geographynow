from __future__ import unicode_literals

from django.db import models
import arrow


class BaseModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Country(BaseModel):
    code = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=100)
    geo_video_url = models.URLField()
    flag_friday_video_url = models.URLField(null=True)

    def __str__(self):
        return self.code.upper()

    @classmethod
    def get_latest_video_info(cls):
        latest_country = Country.objects.all().latest('created_at')
        video_type = 'country video'
        video_added_at = latest_country.created_at
        if latest_country.flag_friday_video_url:
            video_type = 'flag friday video'
            video_added_at = latest_country.updated_at
        return {
            'country': latest_country.name,
            'video_type': video_type,
            'video_added_at_humanized': arrow.get(video_added_at).humanize()
        }
