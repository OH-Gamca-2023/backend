from django.contrib import admin
from django_object_actions import DjangoObjectActions, action

from .models import Post, Tag


@admin.register(Tag)
class TagAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ('id', 'name', 'special')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'special')
    changelist_actions = ('create_default_tags',)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj is not None:
            if not request.user.has_perm('posts.change_special_tag'):
                readonly_fields += ('special',)
        elif not request.user.has_perm('posts.add_special_tag'):
            readonly_fields += ('special',)
        return readonly_fields

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

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.special:
            return super().has_change_permission(request, obj) and request.user.has_perm('posts.change_special_tag')
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.special:
            return super().has_change_permission(request, obj) and request.user.has_perm('posts.delete_special_tag')
        return super().has_delete_permission(request, obj)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'date')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('date',)
    readonly_fields = ('id',)

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.author != request.user:
            return super().has_change_permission(request, obj) and request.user.has_perm('posts.change_others_post')
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.author != request.user:
            return super().has_delete_permission(request, obj) and request.user.has_perm('posts.delete_others_post')
        return super().has_delete_permission(request, obj)