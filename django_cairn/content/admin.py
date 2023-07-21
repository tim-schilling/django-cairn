from django.contrib import admin

from django_cairn.content.models import Post, Source


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ["url", "active", "last_checked", "contact", "type", "updated"]
    list_filter = ["active", "type"]
    ordering = ["url"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "active", "last_checked", "url", "posted", "updated"]
    list_filter = ["active"]
    ordering = ["-posted"]
