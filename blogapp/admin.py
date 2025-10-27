from django.contrib import admin

# Register your models here.
from .models import Blog, Like, Comment

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "author__username")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "blog", "user", "created_at")
    search_fields = ("blog__title", "user__username")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "blog", "user", "created_at")
    search_fields = ("blog__title", "user__username", "content")