from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
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


class PostQuerySet(ActiveQuerySet):
    def tagged_posts(self, tag_slug):
        return self.filter(
            tagged_posts__active=True,
            tagged_posts__tag__active=True,
            tagged_posts__tag__slug=tag_slug,
        )


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
    # Tags
    tags = models.ManyToManyField(
        "Tag", related_name="posts", through="TaggedPost", blank=True
    )
    django_tags = models.ManyToManyField(
        "DjangoTag", related_name="posts", through="DjangoTaggedPost", blank=True
    )

    objects = PostQuerySet.as_manager()

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


class TagManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Tag(TimestampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    active = models.BooleanField(default=False)
    objects = TagManager.from_queryset(ActiveQuerySet)()

    @classmethod
    def slugify(cls, name):
        return slugify(name)

    def natural_key(self):
        return (self.slug,)


class TaggedPost(TimestampedModel):
    tag = models.ForeignKey(Tag, related_name="tagged_posts", on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, related_name="tagged_posts", on_delete=models.CASCADE
    )
    active = models.BooleanField(default=True)
    objects = ActiveQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("tag", "post"),
                name="taggedpost_tag_post_unq",
            )
        ]


class DjangoTagManager(models.Manager):
    def get_by_natural_key(self, version):
        return self.get(version=version)

    def overlapping_versions(self, value: datetime):
        """Get the Django Tags that were valid for the given datetime"""
        return self.filter(released__lte=value, end_of_life__gte=value)


class DjangoTag(TimestampedModel):
    class Version(models.TextChoices):
        v1_3 = "1.3", _("1.3")
        v1_4 = "1.4", _("1.4")
        v1_5 = "1.5", _("1.5")
        v1_6 = "1.6", _("1.6")
        v1_7 = "1.7", _("1.7")
        v1_8 = "1.8", _("1.8")
        v1_9 = "1.9", _("1.9")
        v1_10 = "1.10", _("1.10")
        v1_11 = "1.11", _("1.11")
        v2_0 = "2.0", _("2.0")
        v2_1 = "2.1", _("2.1")
        v2_2 = "2.2", _("2.2")
        v3_0 = "3.0", _("3.0")
        v3_1 = "3.1", _("3.1")
        v4_0 = "4.0", _("4.0")
        v4_1 = "4.1", _("4.1")
        v4_2 = "4.2", _("4.2")
        v5_0 = "5.0", _("5.0")
        v5_1 = "5.1", _("5.1")
        v5_2 = "5.2", _("5.2")
        v6_0 = "6.0", _("6.0")

    version = models.CharField(
        max_length=10,
        choices=Version.choices,
        unique=True,
    )
    # Potentially can switch to DateTimeRangeField
    released = models.DateTimeField()
    end_of_life = models.DateTimeField()
    objects = DjangoTagManager()

    def natural_key(self):
        return (self.version,)


class DjangoTaggedPost(TimestampedModel):
    django_tag = models.ForeignKey(
        DjangoTag, related_name="django_tagged_posts", on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post, related_name="django_tagged_posts", on_delete=models.CASCADE
    )
    active = models.BooleanField(default=True)
    objects = ActiveQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("django_tag", "post"),
                name="djangotaggedpost_djangotag_post_unq",
            )
        ]
