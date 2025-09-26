from django.urls import path

from django_cairn.content.views import (
    DjangoPostListView,
    PostListView,
    TaggedPostListView,
)

app_name = "content"
urlpatterns = [
    path("posts/", view=PostListView.as_view(), name="posts"),
    path(
        "tag/<slug:tag>/posts/", view=TaggedPostListView.as_view(), name="tagged_posts"
    ),
    path("django/", view=DjangoPostListView.as_view(), name="django_posts"),
]
