from datetime import timedelta

from bs4 import BeautifulSoup
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_cairn.utils.models import TimestampedModel


class ActiveQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)


class SourceManager(models.Manager):
    def get_by_natural_key(self, feed_url):
        return self.get(feed_url=feed_url)


class Source(TimestampedModel):
    class Type(models.TextChoices):
        RSS = "rss", _("RSS Feed")

    active = models.BooleanField(default=True)
    url = models.URLField(max_length=2000, unique=True)
    feed_url = models.URLField(max_length=2000, unique=True)
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
    )
    contact = models.EmailField(max_length=500, blank=True)
    author = models.CharField(max_length=256, blank=True)
    title = models.CharField(max_length=500, blank=True)
    last_checked = models.DateTimeField()
    objects = SourceManager.from_queryset(ActiveQuerySet)()

    def reset_feed_properties(self):
        self.last_checked = timezone.now()

    def natural_key(self):
        return (self.feed_url,)


class Post(TimestampedModel):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    body = models.TextField(blank=True)
    posted = models.DateTimeField()
    source = models.ForeignKey(
        Source, related_name="posts", null=True, blank=True, on_delete=models.CASCADE
    )
    url = models.URLField(max_length=2000, unique=True)
    # Feed properties
    last_checked = models.DateTimeField(default=timezone.now)
    next_check = models.DateTimeField(default=timezone.now)
    staleness_count = models.IntegerField(default=0)
    # Search properties
    search_text = models.TextField(blank=True)

    objects = ActiveQuerySet.as_manager()

    def reset_feed_properties(self):
        self.staleness_count = 0
        self.last_checked = timezone.now()
        self.next_check = self.last_checked + timedelta(days=1)

    def reset_search_properties(self):
        soup = BeautifulSoup(self.body, "html.parser")
        self.search_text = " ".join(soup.stripped_strings)

    @property
    def author(self):
        return self.source.author
