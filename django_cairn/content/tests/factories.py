import random
from datetime import datetime, timedelta, timezone

import factory.random
from django.utils.timezone import now
from factory.django import DjangoModelFactory
from faker import Faker

from django_cairn.content.models import DjangoTag, Post, Source, Tag

factory.random.reseed_random("django_cairn")
faker = Faker()
Faker.seed(42)


class SourceFactory(DjangoModelFactory):
    url = factory.Faker("url")
    feed_url = factory.Faker("url")
    type = Source.Type.RSS.value
    author = factory.Faker("name")
    contact = factory.Faker("email")
    last_checked = factory.LazyAttribute(
        lambda a: now() + timedelta(days=random.randint(-30, 0))
    )
    title = factory.LazyAttribute(lambda c: faker.bs().title())

    class Meta:
        model = Source
        django_get_or_create = ["feed_url"]


class PostFactory(DjangoModelFactory):
    url = factory.Faker("url")
    posted = factory.LazyAttribute(
        lambda a: now() + timedelta(days=random.randint(-30, 0))
    )
    source = factory.SubFactory(SourceFactory)
    title = factory.LazyAttribute(lambda c: faker.bs().title())
    body = "<div><p>Hello</p></div>"
    search_text = "Hello"

    class Meta:
        model = Post


class TagFactory(DjangoModelFactory):
    name = factory.Faker("bs")
    slug = factory.LazyAttribute(lambda t: Tag.slugify(t.name))

    class Meta:
        model = Tag


def create_django_tags() -> dict[str, DjangoTag]:
    """Generate the Django Tag data, returns mapping of version to instance"""
    if not DjangoTag.objects.exists():
        date_mapping = {
            DjangoTag.Version.v1_3.value: (
                datetime(2016, 1, 1, tzinfo=timezone.utc),
                datetime(2013, 2, 26, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v1_4.value: (
                datetime(2016, 1, 1, tzinfo=timezone.utc),
                datetime(2015, 10, 1, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v1_5.value: (
                datetime(2016, 1, 1, tzinfo=timezone.utc),
                datetime(2014, 9, 2, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v1_6.value: (
                datetime(2016, 1, 1, tzinfo=timezone.utc),
                datetime(2014, 4, 1, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v1_7.value: (
                datetime(2016, 1, 1, tzinfo=timezone.utc),
                datetime(2015, 12, 1, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v1_8.value: (
                datetime(2016, 1, 1, tzinfo=timezone.utc),
                datetime(2018, 4, 1, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v1_9.value: (
                datetime(2016, 1, 1, tzinfo=timezone.utc),
                datetime(2017, 4, 4, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v1_10.value: (
                datetime(2016, 1, 1, tzinfo=timezone.utc),
                datetime(2017, 12, 2, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v1_11.value: (
                datetime(2016, 1, 1, tzinfo=timezone.utc),
                datetime(2020, 4, 1, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v2_0.value: (
                datetime(2017, 1, 1, tzinfo=timezone.utc),
                datetime(2019, 4, 1, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v2_1.value: (
                datetime(2017, 1, 1, tzinfo=timezone.utc),
                datetime(2019, 12, 2, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v2_2.value: (
                datetime(2017, 1, 1, tzinfo=timezone.utc),
                datetime(2022, 4, 11, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v3_0.value: (
                datetime(2018, 1, 1, tzinfo=timezone.utc),
                datetime(2021, 4, 6, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v3_1.value: (
                datetime(2019, 1, 1, tzinfo=timezone.utc),
                datetime(2021, 12, 7, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v4_0.value: (
                datetime(2021, 1, 1, tzinfo=timezone.utc),
                datetime(2023, 4, 1, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v4_1.value: (
                datetime(2022, 1, 1, tzinfo=timezone.utc),
                datetime(2023, 12, 1, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v4_2.value: (
                datetime(2023, 4, 1, tzinfo=timezone.utc),
                datetime(2026, 4, 1, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v5_0.value: (
                datetime(2023, 12, 1, tzinfo=timezone.utc),
                datetime(2025, 4, 1, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v5_1.value: (
                datetime(2024, 4, 1, tzinfo=timezone.utc),
                datetime(2025, 12, 1, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v5_2.value: (
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                datetime(2028, 4, 1, tzinfo=timezone.utc),
            ),
            DjangoTag.Version.v6_0.value: (
                datetime(2025, 12, 1, tzinfo=timezone.utc),
                datetime(2027, 4, 1, tzinfo=timezone.utc),
            ),
        }
        DjangoTag.objects.bulk_create(
            [
                DjangoTag(version=version, released=released, end_of_life=end_of_life)
                for version, (released, end_of_life) in date_mapping.items()
            ]
        )
    return dict(DjangoTag.objects.in_bulk(field_name="version"))
