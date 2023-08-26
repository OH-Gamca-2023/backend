from datetime import datetime

from django.db import connections
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView


class StatusView(APIView):
    def get(self, request):
        start_time = datetime.now()
        data = {
            "status": "ok",
            "time": datetime.now().isoformat(),
            "authenticated": request.user.is_authenticated,
            'database_status': 'check_disabled'  # self.check_database_status(),
        }
        end_time = datetime.now()
        data['execution_time'] = str(end_time - start_time)
        return Response(data, status=status.HTTP_200_OK)

    def check_database_status(self):
        database_status = {}
        for db_name in connections:
            connection = connections[db_name]
            try:
                connection.ensure_connection()
                database_status[db_name] = {
                    'status': True,
                    'is_usable': connection.is_usable(),
                }
            except Exception as e:
                database_status[db_name] = False
        return database_status


def home(request):
    return HttpResponse(status=302, headers={'Location': '/admin/'})


@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'Nehrajte sa so stránkou, jediné čo z toho viete dostať je IP ban.',
    })
