from django.contrib import admin

from .models import Post, Comment, Tag

admin.site.register(Post)
admin.site.register(Comment)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
