from django.core.management.base import BaseCommand
from webmap.pipeline import update_country_info


class Command(BaseCommand):
    help = 'Pull and Process Geography youtube video info'

    def handle(self, *args, **options):
        update_country_info()
        self.stdout.write(self.style.SUCCESS('Successfully info updated'))
