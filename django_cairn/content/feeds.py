import feedparser
from dateutil.parser import parse as dateutil_parser

from django_cairn.content.models import Post, Source

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
            post = Post.objects.filter(url=entry["link"]).first()
            if not post:
                post = Post(source=source, url=entry["link"])
            post.reset_feed_properties()
            if not entry["title"] or not entry.get("published"):
                continue
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
