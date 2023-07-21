from django.views.generic import ListView

from django_cairn.content.models import Post


class PostListView(ListView):
    model = Post
    ordering = ["-posted"]
    queryset = Post.objects.active().select_related("source")
    template_name = "content/posts.html"
    paginate_by = 50
