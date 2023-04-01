from django.http import JsonResponse

from messages.common import get_message


def client_error(status: int, message_code: str, *args):
    if status < 400 or status > 499:
        raise ValueError("Status code must be in the 400-499 range")

    args = tuple(map(str, args))
    message = get_message("error." + message_code)
    message = message % args

    return JsonResponse({
        "status": status,
        "error": True,
        "internalError": False,
        "errorCode": message_code,
        "errorMessage": message
    }, status=status)


def not_authenticated():
    return client_error(401, "not_authenticated")


def invalid_method(allowed_methods: list):
    return client_error(405, "invalid_method", ", ".join(allowed_methods))


def server_error(status: int, message_code: str, *args):
    if status < 500 or status > 599:
        raise ValueError("Status code must be in the 500-599 range")

    if not message_code.startswith("server."):
        message_code = "server." + message_code

    args = tuple(map(str, args))
    message = get_message("error." + message_code)
    message = message % args

    return JsonResponse({
        "status": status,
        "error": True,
        "internalError": True,
        "errorCode": message_code,
        "errorMessage": message
    }, status=status)
