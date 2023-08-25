import feedparser
from dateutil.parser import parse as dateutil_parser

from django_cairn.content.models import Post, Source, Tag

POST_MAPPING = {
    "url": "link",
    "title": "title",
}

SOURCE_MAPPING = {
    "title": "title",
    "url": "link",
}


class UnexpectedSummaryType(Exception):
    pass


def fetch_from_source(source: Source):
    response = feedparser.parse(source.feed_url)
    # If the version isn't set, it's likely a plain page and not a feed.
    if "version" not in response:
        breakpoint()
    if response.get("version"):
        for entry in response["entries"]:
            if not entry["title"] or not entry.get("published"):
                continue
            post = Post.objects.filter(url=entry["link"]).first()
            if not post:
                post = Post(source=source, url=entry["link"])
            post.reset_feed_properties()
            post.posted = dateutil_parser(entry["published"])
            if "content" in entry:
                post.body = entry["content"][0]["value"]
                post.description = entry["summary"]
            else:
                post.description = ""
                summary = entry["summary_detail"]
                if summary["type"] != "text/html":
                    raise UnexpectedSummaryType(
                        "Found unexpected summary type %s" % summary["type"]
                    )
                post.body = summary["value"]

            for field, feed in POST_MAPPING.items():
                setattr(post, field, entry[feed])
            post.reset_search_properties()
            post.save()

            tag_name_mapping = {
                Tag.slugify(tag_name): tag_name
                for tag in entry.get("tags", [])
                if tag.get("term") and (tag_name := tag["term"].strip())
            }
            post_tag_queryset = Tag.objects.filter(slug__in=tag_name_mapping.keys())
            # Look up any existing tags to reduce the number of conflicts on insert
            existing_tags = set(post_tag_queryset.values_list("slug", flat=True))
            # Attempt to insert any new tags.
            Tag.objects.bulk_create(
                [
                    Tag(name=name, slug=slug)
                    for slug, name in tag_name_mapping.items()
                    if slug not in existing_tags
                ],
                # While we are attempting to prevent inserting existing tags,
                # a web request to the admin could create a tag at the same
                # exact time. If that occurs, it's fine as long as the row gets
                # inserted.
                ignore_conflicts=True,
            )
            # Update the post's associated tags
            post.tags.set(post_tag_queryset)

        feed = response["feed"]
        for field, feed_field in SOURCE_MAPPING.items():
            setattr(source, field, feed[feed_field])
        source.author = feed.get("author_detail", {}).get("name") or source.author
        source.contact = feed.get("author_detail", {}).get("email") or source.contact

    source.reset_feed_properties()
    source.save()


def fetch_content():
    for source in Source.objects.active():
        fetch_from_source(source)
