from django.contrib import admin
from django.db.models import Count

from django_cairn.content.models import DjangoTag, Post, Source, Tag


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ["url", "active", "last_checked", "contact", "type", "updated"]
    list_filter = ["active", "type"]
    ordering = ["url"]
    search_fields = ["feed_url", "author", "title"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "active", "last_checked", "url", "posted", "updated"]
    list_filter = ["active"]
    ordering = ["-posted"]
    autocomplete_fields = ["source"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "active", "usages"]
    search_fields = ["slug"]
    list_filter = ["active"]
    ordering = ["slug"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(post_count=Count("tagged_posts"))

    @admin.display(ordering="post_count")
    def usages(self, obj):
        return obj.post_count


@admin.register(DjangoTag)
class DjangoTagAdmin(admin.ModelAdmin):
    list_display = ["version", "released", "end_of_life", "usages"]
    ordering = ["-version"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(post_count=Count("django_tagged_posts"))
        )

    @admin.display(ordering="post_count")
    def usages(self, obj):
        return obj.post_count
