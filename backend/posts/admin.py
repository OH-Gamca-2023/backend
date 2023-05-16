from django.contrib import admin

from .models import Post, Comment, Tag

admin.site.register(Comment)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'date', 'disable_comments')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('date', 'disable_comments')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_admin or request.user.has_perm('posts.change_other_posts'):
            return qs
        return qs.filter(author=request.user)
