from django.http import JsonResponse
from rest_framework.views import APIView

from disciplines.models import Category, Discipline
from disciplines.serializers import CategorySerializer, DisciplineSerializer


class CategoriesListApiView(APIView):

    def get(self, request):
        serializer = CategorySerializer(Category.objects.all(), many=True)
        return JsonResponse(serializer.data, safe=False)


class DisciplineListApiView(APIView):

    def get(self, request):
        # parse query params
        category_id = request.GET.get('category', None)
        grade_id = request.GET.get('grade', None)
        if grade_id is not None:
            grade_id = grade_id.split(',')

        # filter disciplines
        disciplines = Discipline.objects.all()
        if category_id is not None:
            disciplines = disciplines.filter(category_id=category_id)
        if grade_id is not None:
            disciplines = disciplines.filter(target_grades__in=grade_id)

        # serialize
        serializer = DisciplineSerializer(disciplines, many=True)
        return JsonResponse(serializer.data, safe=False)


class DisciplineApiView(APIView):

        def get(self, request, id):
            discipline = Discipline.objects.get(id=id)
            serializer = DisciplineSerializer(discipline)
            return JsonResponse(serializer.data, safe=False)