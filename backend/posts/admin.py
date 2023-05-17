from django.contrib import admin

from .models import Post, Comment, Tag

admin.site.register(Comment)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'special')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'special')

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        return ('special',)


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
