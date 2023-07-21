from django.core.management.base import BaseCommand

from django_cairn.content.feeds import fetch_content


class Command(BaseCommand):
    help = "Fetch content from sources."

    def handle(self, **options):
        fetch_content()
