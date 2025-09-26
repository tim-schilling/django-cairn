from datetime import datetime, timedelta

import pytest
from django.utils import timezone

from django_cairn.content.models import DjangoTag, Post, Source, Tag
from django_cairn.content.tests import factories
from django_cairn.content.tests.factories import TagFactory, create_django_tags

pytestmark = pytest.mark.django_db


class TestActiveQuerySet:
    @pytest.mark.parametrize(
        "factory",
        [
            factories.SourceFactory,
            factories.PostFactory,
            factories.TagFactory,
        ],
    )
    def test_active(self, factory):
        active = factory.create(active=True)
        factory.create(active=False)
        assert factory._meta.model.objects.count() == 2
        assert factory._meta.model.objects.active().get() == active


class TestSourceManager:
    def test_get_by_natural_key(self):
        source = factories.SourceFactory.create()
        assert Source.objects.get_by_natural_key(source.feed_url) == source


class TestSource:
    def test_reset_feed_properties(self):
        source = factories.SourceFactory.create(
            last_checked=timezone.now() - timedelta(days=1)
        )
        previous = source.last_checked
        source.reset_feed_properties()
        assert source.last_checked > previous
        # Confirm the source wasn't saved.
        assert Source.objects.get(id=source.id).last_checked == previous

    def test_natural_key(self):
        source = factories.SourceFactory.create(
            feed_url="https://django-cairn.org/atom.xml"
        )
        assert source.natural_key() == ("https://django-cairn.org/atom.xml",)


class TestPostQuerySet:
    def test_tagged_posts(self):
        active_tag1, active_tag2 = factories.TagFactory.create_batch(2, active=True)
        inactive_tag = factories.TagFactory.create(active=False)
        post = factories.PostFactory.create()
        post.tags.set([active_tag1, active_tag2, inactive_tag])
        post.tagged_posts.filter(tag=active_tag2).update(active=False)
        assert Post.objects.tagged_posts(active_tag1.slug).get() == post
        assert not Post.objects.tagged_posts(active_tag2.slug).exists()
        assert not Post.objects.tagged_posts(inactive_tag.slug).exists()


class TestPost:
    def test_reset_feed_properties(self):
        post = factories.PostFactory.create(
            last_checked=timezone.now() - timedelta(days=1),
            staleness_count=1,
            next_check=timezone.now(),
        )
        previous_last_checked = post.last_checked
        previous_next_check = post.next_check

        post.reset_feed_properties()
        assert post.last_checked > previous_last_checked
        assert post.next_check > previous_next_check
        assert post.next_check == post.last_checked + timedelta(days=1)
        assert post.staleness_count == 0
        # Confirm the post wasn't saved.
        assert Post.objects.get(id=post.id).last_checked == previous_last_checked

    def test_author(self):
        post = factories.PostFactory.create()
        assert post.author == post.source.author

    def test_reset_search_properties(self):
        post = factories.PostFactory.create(
            body="<p>This is a test.</p><span>Who writes html by hand?</span>"
        )
        previous_search_text = post.search_text
        post.reset_search_properties()
        assert post.search_text == "This is a test. Who writes html by hand?"
        # Confirm the post wasn't saved.
        assert Post.objects.get(id=post.id).search_text == previous_search_text


class TestDjangoTagManager:
    def test_get_by_natural_key(self):
        django_tag = next(iter(create_django_tags().values()))
        assert DjangoTag.objects.get_by_natural_key(django_tag.version) == django_tag

    def test_overlapping_versions(self):
        django_tags = create_django_tags()
        v1 = django_tags[DjangoTag.Version.v1_11]
        v3_2 = django_tags[DjangoTag.Version.v3_2]
        v5_0 = django_tags[DjangoTag.Version.v5_0]

        def get_versions(value: datetime):
            return list(
                DjangoTag.objects.overlapping_versions(value)
                .values_list("version", flat=True)
                .order_by("version")
            )

        assert get_versions(v1.released) == [DjangoTag.Version.v1_11]
        assert get_versions(v3_2.released) == [
            DjangoTag.Version.v3_0,
            DjangoTag.Version.v3_1,
            DjangoTag.Version.v3_2,
        ]
        assert get_versions(v5_0.end_of_life) == [DjangoTag.Version.v5_0]


class TestDjangoTag:
    def test_natural_key(self):
        django_tag = next(iter(create_django_tags().values()))
        assert django_tag.natural_key() == ("1.11",)


class TestTagManager:
    def test_get_by_natural_key(self):
        tag = TagFactory.create()
        assert Tag.objects.get_by_natural_key(tag.slug) == tag


class TestTag:
    def test_natural_key(self):
        tag = TagFactory.create()
        assert tag.natural_key() == (tag.slug,)

    def test_slugify(self):
        assert Tag.slugify("Hello World") == "hello-world"
