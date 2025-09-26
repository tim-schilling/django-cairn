from django.views.generic import ListView

from django_cairn.content.models import DjangoTag, Post


class PostListView(ListView):
    model = Post
    ordering = ["-posted"]
    queryset = Post.objects.active().select_related("source")
    template_name = "content/posts.html"
    paginate_by = 50


class TaggedPostListView(PostListView):
    def get_queryset(self):
        return super().get_queryset().tagged_posts(tag=self.kwargs["tag"])


class DjangoPostListView(PostListView):
    """Return the Django posts specifically.

    This allows for the tags to be specified in the URL bar.
    """

    queryset = PostListView.queryset.django()
    _versions = None

    @property
    def selected_versions(self):
        if self._versions is None:
            self._versions = []
            if raw_versions := self.request.GET.getlist("versions"):
                for raw_version in raw_versions:
                    try:
                        self._versions.append(DjangoTag.Version(raw_version))
                    except ValueError:
                        # The version wasn't a valid version.
                        continue
        return self._versions

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.selected_versions:
            queryset = queryset.for_django_versions(versions=self.selected_versions)
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data()
        context.update(
            {
                "selected_versions": self.selected_versions,
                "versions": self.versions,
            }
        )
        return context
