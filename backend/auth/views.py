import traceback

from django.contrib import messages
from django.contrib.auth import logout, login
from django.http import HttpResponseRedirect
from rest_framework import permissions
from rest_framework.views import APIView
from knox.views import LoginView as KnoxLoginView
import json

from users.serializers import UserSerializer
from .oauth_helper import get_sign_in_flow, get_token_from_code, remove_user_and_token, settings
from .graph_helper import *
from .user_helper import handle_user_login


def initialize_context(request):
    context = {}
    error = request.session.pop('flash_error', None)
    if error is not None:
        context['errors'] = []
    context['errors'].append(error)
    # Check for user in the session
    context['user'] = request.session.get('user', {'is_authenticated': False})

    return context


class OauthStartView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
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


class OauthAdminStartView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        # Get the sign-in flow
        flow = get_sign_in_flow(settings['admin_redirect'])
        # Save the expected flow so we can use it in the callback
        try:
            request.session['admin_auth_flow'] = flow
        except Exception as e:
            print(e)
        # Redirect to the Azure sign-in page
        response = HttpResponseRedirect(flow['auth_uri'])
        response['Cross-Origin-Opener-Policy'] = 'unsafe-none'
        return response


class OauthCallbackView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        try:
            # Make the token request
            result = get_token_from_code(request)
            # Get the user's profile from graph_helper.py script
            user = get_user(result['access_token'])

            logged_user = handle_user_login(request, user)
            login(request, logged_user)

            response = super(OauthCallbackView, self).post(request, format=None)
            print(response)
            if response.status_code == 200:
                serialized_user_token = json.dumps(response.data)
                serialized_logged_user = json.dumps(UserSerializer(logged_user).data)

                url_params = '?status=success&user_token=' + serialized_user_token + '&logged_user=' + serialized_logged_user
                return HttpResponseRedirect(settings['fe_redirect'] + url_params)
            else:
                url_params = '?status=error&error=' + str(response.data)
                return HttpResponseRedirect(settings['fe_redirect'] + url_params)
        except Exception as e:
            traceback.print_exc()

            # If something goes wrong, logout the user
            remove_user_and_token(request)
            logout(request)

            url_params = '?status=error&error=' + str(e)
            return HttpResponseRedirect(settings['fe_redirect'] + url_params)


class OauthAdminCallbackView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        try:
            # Make the token request
            result = get_token_from_code(request, 'admin_auth_flow')
            # Get the user's profile from graph_helper.py script
            user = get_user(result['access_token'])

            logged_user = handle_user_login(request, user, True)
            login(request, logged_user)

            return HttpResponseRedirect(settings['admin_login_redirect'])
        except Exception as e:
            # If something goes wrong, logout the user, just in case
            logout(request)

            messages.error(request, e)
            return HttpResponseRedirect(settings['admin_login_redirect'])
