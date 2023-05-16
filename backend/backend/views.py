from datetime import datetime

from django.http import JsonResponse, HttpResponse


def status(request):
    response = {
        "status": "ok",
        "time": datetime.now().isoformat(),
        "authenticated": request.user.is_authenticated,
    }

    return JsonResponse(response)


def home(request):
    return HttpResponse(status=302, headers={'Location': '/admin/'})