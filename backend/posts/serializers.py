from rest_framework import serializers

from posts.models import Tag, Post
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(hide_personal=True)
    content = serializers.CharField(source='parsed_content', read_only=True, trim_whitespace=False)

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author', 'date', 'related_disciplines', 'affected_grades', 'tags')
