from django.http import JsonResponse
from rest_framework.views import APIView

from posts.models import Tag, Post
from posts.serializers import TagSerializer, PostSerializer


# Create your views here.

class TagListAPIView(APIView):

    def get(self, request):
        serializer = TagSerializer(Tag.objects.all(), many=True)
        return JsonResponse(serializer.data, safe=False)


class PostListAPIView(APIView):

    def get(self, request):
        serializer = PostSerializer(Post.objects.all(), many=True)
        return JsonResponse(serializer.data, safe=False)