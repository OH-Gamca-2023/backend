from django.http import JsonResponse

from disciplines.models import Category
from disciplines.serializers import CategorySerializer


def categories(request):
    serializer = CategorySerializer(Category.objects.all(), many=True)

    return JsonResponse(serializer.data, safe=False)