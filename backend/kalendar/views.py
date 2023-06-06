from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from kalendar.models import Calendar


def http_cache_date(millis):
    """
    Convert milliseconds to a date in HTTP cache format.
    """
    date = timezone.datetime.fromtimestamp(float(millis) / 1000.0, tz=timezone.utc)
    return date.strftime('%a, %d %b %Y %H:%M:%S GMT')


def handle_cache(request):
    response = HttpResponse()

    current = Calendar.objects.get(key="current")
    if current is None:
        return JsonResponse({'error': 'not_ready'}, status=503)
    response['ETag'] = current.id
    response['Last-Modified'] = http_cache_date(current.content)
    response['Cache-Control'] = 'max-age=0, must-revalidate'

    if 'HTTP_IF_NONE_MATCH' in request.META:
        if request.META['HTTP_IF_NONE_MATCH'] == current.id:
            response.status_code = 304
            return response, False
    elif 'HTTP_IF_MODIFIED_SINCE' in request.META:
        if request.META['HTTP_IF_MODIFIED_SINCE'] == http_cache_date(current.content):
            response.status_code = 304
            return response, False

    return response, True


def handle(request, type):
    response, should_generate = handle_cache(request)
    if should_generate:
        content = Calendar.objects.get(key=type)
        if content is None:
            return JsonResponse({'error': 'not_ready'}, status=503)
        response['Content-Type'] = content.content_type
        response.content = content.content
    return response


def json_default(request):
    return handle(request, "disciplines_json")


def json_staff(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
    if not request.user.is_staff and not request.user.clazz.grade.is_teacher:
        return JsonResponse({'detail': 'You do not have permission to perform this action.'}, status=403)
    return handle(request, "staff_only_json")


def json_all(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
    if not request.user.is_staff and not request.user.clazz.grade.is_teacher:
        return JsonResponse({'detail': 'You do not have permission to perform this action.'}, status=403)
    return handle(request, "all_json")


def json_auto(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.clazz.grade.is_teacher):
        return json_all(request)
    return json_default(request)


def ical_default(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
    if not request.user.is_staff and not request.user.clazz.grade.is_teacher:
        return JsonResponse({'detail': 'You do not have permission to perform this action.'}, status=403)
    return handle(request, "disciplines_ical")


def ical_staff(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
    if not request.user.is_staff and not request.user.clazz.grade.is_teacher:
        return JsonResponse({'detail': 'You do not have permission to perform this action.'}, status=403)
    return handle(request, "staff_only_ical")


def ical_all(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
    if not request.user.is_staff and not request.user.clazz.grade.is_teacher:
        return JsonResponse({'detail': 'You do not have permission to perform this action.'}, status=403)
    return handle(request, "all_ical")