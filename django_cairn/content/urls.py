from django.urls import path

from django_cairn.content.views import PostListView

app_name = "content"
urlpatterns = [
    path("posts/", view=PostListView.as_view(), name="posts"),
]
