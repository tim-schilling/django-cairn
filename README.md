# Django Cairn
*The passive trail guide for a Djangonaut's journey.*

This is the future home to the source code for a web site dedicated to
cataloging Django knowledge across the web.

The current plan is as follows:

1. Collect initial static content links, titles and descriptions.
2. Categorize content.
3. Determine UX and UI.
4. Determine data model.
6. Implement views and templates.
7. `<deployment shenanigans>`
8. Research RSS ingestion solution.
9. Research content review solution.
10. `<draw rest of owl>`

If you'd like to help, I'd love to have it. But as you can see, things are
still a bit mushy.

If you're still interested, add a comment to
[Issue #2](https://github.com/tim-schilling/django-cairn/issues/2).

If you have specific ideas for the site, feel free to share them with me
how you're most comfortable. The best public location is currently the
[welcome discussion](https://github.com/tim-schilling/django-cairn/discussions/1).


# Design Document

I wrote a [blog post](https://www.better-simple.com/django/cairn/2023/02/28/plotting-the-trail-for-django-cairn/)
detailing the process of this design that may be useful.

## Content sources

- RSS feed reader integration
- DjangoCon Jekyll file parser
- Django newsletter comments
- Helpful social media links
- Helpful gists

## Models

**Content**
- title
- description
- tags
- posted
- published
- source
- url
- image
- thumbnail
- last updated
- last checked
- parsed content
- search content
- next check
- staleness count

**Source**
- url
- title
- last updated
- last checked
- contact
- active

**Tag**
- title

**DjangoVersionTag**

**PythonVersionTag**

**ContentReview(historical)**
- content
- user
- published
- publish date
- created
- updated
- review
- recommend
- rating
- reader level (beginner, intermediate, expert, all)

**ReviewRequest**

**FetchSourceSnapshot**
- created
- updated
- state
- date
- source

**FetchContentSnapshot**
- created
- updated
- content
- state

## Views

**Landing**
- show latest content
- show latest reviewed content
- submit new source
- submit new content
- request to be curator
- search

**Submit new source**
- url
- title
- contact
- reason

**Submit new content**
- url
- django versions
- python versions
- source title
- contact
- reason

**Request to be curator** (email)

**Report curation** (email?)

**Search**
- full text search
- filter on django tags
- filter on python tags
