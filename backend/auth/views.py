from django.contrib.auth import logout
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .oauth_helper import get_sign_in_flow, get_token_from_code, store_user, remove_user_and_token, settings
from .graph_helper import *
from .user_helper import handle_user_login, create_user_token


def initialize_context(request):
    context = {}
    error = request.session.pop('flash_error', None)
    if error is not None:
        context['errors'] = []
    context['errors'].append(error)
    # Check for user in the session
    context['user'] = request.session.get('user', {'is_authenticated': False})

    return context


def sign_in(request):
    # Get the sign-in flow
    flow = get_sign_in_flow()
    # Save the expected flow so we can use it in the callback
    try:
        request.session['auth_flow'] = flow
    except Exception as e:
        print(e)
    # Redirect to the Azure sign-in page
    response = HttpResponseRedirect(flow['auth_uri'])
    response['Cross-Origin-Opener-Policy'] = 'unsafe-none'
    return response


def sign_out(request):
    # Clear out the user and token
    remove_user_and_token(request)
    response = HttpResponseRedirect(reverse('home'))
    response['Cross-Origin-Opener-Policy'] = 'unsafe-none'
    return response


def callback(request):
    try:
        # Make the token request
        result = get_token_from_code(request)
        # Get the user's profile from graph_helper.py script
        user = get_user(result['access_token'])
        # Store user from auth_helper.py script
        store_user(request, user)

        logged_user = handle_user_login(request, user)

        user_token = create_user_token(request, logged_user)

        # serialize user_token and logged_user to json and send to frontend
        serialized_user_token = serializers.serialize('json', [user_token])
        serialized_logged_user = serializers.serialize('json', [logged_user])

        url_params = '?status=success&user_token=' + serialized_user_token + '&logged_user=' + serialized_logged_user
        return HttpResponseRedirect(settings['fe_redirect'] + url_params)
    except Exception as e:
        print(e)

        # If something goes wrong, logout the user
        remove_user_and_token(request)
        logout(request)

        url_params = '?status=error&error=' + str(e)
        return HttpResponseRedirect(settings['fe_redirect'] + url_params)


@csrf_exempt
def invalidate(request):
    if not request.method == 'DELETE':
        return HttpResponse(status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'not authenticated'}, status=401)

    token = request.token
    if token:
        token.invalid = True
        token.save()
        return HttpResponse(status=204)
    else:
        return JsonResponse({'error': 'no token present'}, status=400)
