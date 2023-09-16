import os
from datetime import datetime

from django.db import connections
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView

from django.views import generic
from django.conf import settings
from django.http import JsonResponse
from mdeditor.configs import MDConfig


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


MDEDITOR_CONFIGS = MDConfig('default')


class UploadView(generic.View):

    def post(self, request, *args, **kwargs):
        upload_image = request.FILES.get("editormd-image-file", None)
        media_root = settings.MEDIA_ROOT

        # image none check
        if not upload_image:
            return JsonResponse({
                'success': 0,
                'message': "The image to be uploaded was not obtained",
                'url': ""
            })

        # image format check
        file_name_list = upload_image.name.split('.')
        file_extension = file_name_list.pop(-1)
        file_name = '.'.join(file_name_list)
        if file_extension not in MDEDITOR_CONFIGS['upload_image_formats']:
            return JsonResponse({
                'success': 0,
                'message': "The uploaded image format is wrong. The allowed image formats to be uploaded are: %s" % ','.join(
                    MDEDITOR_CONFIGS['upload_image_formats']),
                'url': ""
            })

        # image folder check
        file_path = os.path.join(media_root, MDEDITOR_CONFIGS['image_folder'])
        if not os.path.exists(file_path):
            try:
                os.makedirs(file_path)
            except Exception as err:
                return JsonResponse({
                    'success': 0,
                    'message': "Upload failed: %s" % str(err),
                    'url': ""
                })

        # save image
        file_full_name = '%s_%s.%s' % (file_name.replace(' ', '_'),
                                       '{0:%Y%m%d%H%M%S%f}'.format(datetime.now()),
                                       file_extension)
        with open(os.path.join(file_path, file_full_name), 'wb+') as file:
            for chunk in upload_image.chunks():
                file.write(chunk)

        return JsonResponse({'success': 1,
                             'message': "Upload successful!",
                             'url': os.path.join(settings.MEDIA_URL,
                                                 file_full_name)})
