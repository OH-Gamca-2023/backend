from rest_framework import serializers

from posts.models import Tag, Post
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(hide_confidential=True)

    class Meta:
        model = Post
        fields = '__all__'
