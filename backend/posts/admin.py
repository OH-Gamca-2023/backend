from django.contrib import admin
from django_object_actions import DjangoObjectActions, action

from .models import Post, Comment, Tag

admin.site.register(Comment)


@admin.register(Tag)
class TagAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ('id', 'name', 'special')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'special')
    changelist_actions = ('create_default_tags',)

    def get_readonly_fields(self, request, obj=None):
        if request.user.has_perm('posts.change_special_tags'):
            return ()
        return ('special',)

    @action(description="Vytvoriť predvolené tagy", permissions=['add'])
    def create_default_tags(self, request, queryset):
        default_tags = [
            ("Výsledky", "results"),
            ("Detaily", "info"),
        ]
        for name, special in default_tags:
            tag = Tag.objects.filter(special=special).first()
            if tag is None:
                tag = Tag(name=name, special=special)
                tag.save()


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'date', 'disable_comments')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('date', 'disable_comments')
    readonly_fields = ('id', 'disable_comments')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_admin or request.user.has_perm('posts.change_other_posts'):
            return qs
        return qs.filter(author=request.user)
