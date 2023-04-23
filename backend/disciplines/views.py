from django.http import JsonResponse

from backend.disciplines.models import Category
from backend.disciplines.serializers import CategorySerializer


def categories(request):
    serializer = CategorySerializer(Category.objects.all(), many=True)

    return JsonResponse(serializer.data, safe=False)