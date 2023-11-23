from rest_framework import serializers

from backend.posts.models import Tag, Post
from backend.users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(hide_personal=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'safe', 'redirect', 'author', 'date', 'related_disciplines', 'affected_grades', 'tags')
