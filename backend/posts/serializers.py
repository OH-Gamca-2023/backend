from rest_framework import serializers

from posts.models import Tag, Post
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(hide_personal=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author', 'date', 'related_disciplines', 'affected_grades', 'tags')
