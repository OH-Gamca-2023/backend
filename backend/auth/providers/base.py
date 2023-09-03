import json
import traceback
import urllib.parse

from django.contrib import messages
from django.contrib.auth import login, user_logged_in
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import DateTimeField

from backend.data.models import AuthRestriction
from backend.users.models import User

from knox.models import AuthToken
from knox.settings import knox_settings

from backend.users.serializers import UserSerializer


class TokenProvider:
    def get_token_ttl(self):
        return knox_settings.TOKEN_TTL

    def get_token_limit_per_user(self):
        return knox_settings.TOKEN_LIMIT_PER_USER

    def get_user_serializer_class(self):
        return knox_settings.USER_SERIALIZER

    def get_expiry_datetime_format(self):
        return knox_settings.EXPIRY_DATETIME_FORMAT

    def format_expiry_datetime(self, expiry):
        datetime_format = self.get_expiry_datetime_format()
        return DateTimeField(format=datetime_format).to_representation(expiry)

    def create_token(self, request, user):
        token_limit_per_user = self.get_token_limit_per_user()
        if token_limit_per_user is not None:
            now = timezone.now()
            token = user.auth_token_set.filter(expiry__gt=now)
            if token.count() >= token_limit_per_user:
                return Response(
                    {"error": "Maximum amount of tokens allowed per user exceeded."},
                    status=status.HTTP_403_FORBIDDEN
                )
        token_ttl = self.get_token_ttl()
        instance, token = AuthToken.objects.create(user, token_ttl)
        user_logged_in.send(sender=user.__class__,
                            request=request, user=user)
        return {
            'expiry': self.format_expiry_datetime(instance.expiry),
            'token': token
        }

class OauthProvider:
    name = None
    oauth_user_model = None
    user_property = None

    token_provider = TokenProvider()

    def __init__(self):
        if self.name is None:
            raise ImproperlyConfigured(
                'OauthProvider must be configured with name'
            )
        if (self.oauth_user_model is not None and self.user_property is None) or \
                (self.oauth_user_model is None and self.user_property is not None):
            raise ImproperlyConfigured(
                'OauthProvider must be configured either with both oauth_user_model and user_property or neither'
            )

    def start_flow(self, request, callback_url):
        raise ImproperlyConfigured(
            'OauthProvider must override start_flow method'
        )

    def get_service_url(self, request, flow, callback_url):
        raise ImproperlyConfigured(
            'OauthProvider must override get_service_url method'
        )

    def get_oauth_user(self, request, flow):
        raise ImproperlyConfigured(
            'OauthProvider must override get_oauth_user method'
        )

    def get_verification_oauth_user(self, request):
        raise ImproperlyConfigured(
            'OauthProvider must override verify_oauth_user method'
        )

    def get_user_props(self, request, flow, oauth_user=None):
        raise ImproperlyConfigured(
            "OauthProvider must override get_user_props method"
        )

    def get_verification_user_props(self, request, oauth_user=None):
        raise ImproperlyConfigured(
            "OauthProvider must override verify_user_props method"
        )

    def format_callback_query(self, request):
        return "?" + request.GET.urlencode()

    def begin(self, request):
        callback_url = request.build_absolute_uri(reverse('auth:oauth_callback', kwargs={'service': self.name}))
        if request.GET:
            callback_url += self.format_callback_query(request)

        flow = self.start_flow(request, callback_url)
        session_data = {
            "type": self.name,
            "flow": flow,
            "params": request.GET.dict(),
        }

        request.session['oauth'] = session_data

        service_url = self.get_service_url(request, flow, callback_url)
        return HttpResponseRedirect(service_url)

    def callback(self, request):
        try:
            session_data = request.session.get('oauth')
            if session_data is None:
                return Response({"detail": "No oauth session data found"}, status=400)

            if session_data['type'] != self.name:
                return Response({"detail": "Invalid oauth session type"}, status=400)

            params = request.GET.dict()
            if session_data['params']:
                # Add params from session to params from request
                params.update(session_data['params'])
            def respond(data, status):
                response = params["response"] if "response" in params else "default"
                next = params["next"] if "next" in params else None

                def create_message():
                    if data and data["status"] and data["status"] == "success":
                        if data['logged_user']:
                            messages.success(request, f"Boli ste úspešne prihlásený ako {data['logged_user']['username']}")
                        else:
                            messages.success(request, "Akcia prebehla úspešne")
                    else:
                        messages.error(request, f"Nastala chyba: {data['message']}")

                if next:
                    if next[0] == "/":
                        next = request.build_absolute_uri(next)

                    if response == "omit":
                        return HttpResponseRedirect(next)
                    elif response == "message":
                        create_message()
                        return HttpResponseRedirect(next)
                    else:
                        next += "&" if "?" in next else "?"
                        stringified_data = {k: json.dumps(v) if (isinstance(v, dict) or isinstance(v, list)) else str(v) for
                                            k, v in data.items() if v is not None}
                        next += urllib.parse.urlencode(stringified_data)
                        return HttpResponseRedirect(next)
                else:
                    if response == "omit":
                        return HttpResponse(status=status)
                    elif response == "message":
                        create_message()
                        return HttpResponse(status=status)
                    else:
                        return Response(data, status=status)

            try:
                flow = session_data['flow']
                if self.oauth_user_model is not None:
                    oauth_user = self.get_oauth_user(request, flow)
                    try:
                        user = User.objects.get(**{self.user_property: oauth_user})
                    except User.DoesNotExist:
                        restriction = self.check_restriction(request, 'register', **self.get_check_params(request, oauth_user=oauth_user))
                        if restriction is not None:
                            return respond({"status": "error", "message": f"STRERROR: {restriction}"}, 403)
                        user_props = self.get_user_props(request, flow, oauth_user)
                        if not self.user_property in user_props:
                            user_props[self.user_property] = oauth_user
                        user = User.objects.create(**user_props)
                else:
                    user_props = self.get_user_props(request, flow)
                    try:
                        user = User.objects.get(email=user_props["email"])
                    except User.DoesNotExist:
                        restriction = self.check_restriction(request, 'register', **self.get_check_params(request, user_props=user_props))
                        if restriction is not None:
                            return respond({"status": "error", "message": f"STRERROR: {restriction}"}, 403)
                        user = User.objects.create(**user_props)

                restriction = self.check_restriction(request, 'login', user)
                if restriction is not None:
                    return respond({"status": "error", "message": f"STRERROR: {restriction}"}, 403)

                if not user.is_active:
                    return respond({"status": "error", "message": f"STRERROR: Váš účet bol deaktivovaný"}, 403)

                response, status = self.log_user_in(request, user, request.GET.dict())
                return respond(response, status)

            except Exception as e:
                traceback.print_exc()
                # Attempt to respond in requested format
                return respond({"status": "error", "message": f"{e}"}, 500)
        except Exception as e:
            traceback.print_exc()
            # Return error as JSON in case proper response was not possible to generate
            return Response({"status": "error", "message": f"{e}"}, 500)

    def check_restriction(self, request, type, user=None, microsoft_department=None):
        print(f"Checking restriction {type} for user {user.username if user else '[anon]'} in department {microsoft_department}.")
        if type not in ['register', 'login']:
            raise Exception('Invalid type.')

        try:
            restriction = AuthRestriction.objects.get(type=type)
            if not restriction.restricted:
                return None

            user_str = f"[{user.username}#{user.id}]" if user else "[anon]"

            if restriction.full:
                return restriction.message

            if user:
                if restriction.bypass_staff and user.is_staff:
                    print(f"Restriction {type} bypassed for staff user {user_str}.")
                    return None
                if restriction.bypass_superuser and user.is_superuser:
                    print(f"Restriction {type} bypassed for superuser {user_str}.")
                    return None
            if microsoft_department:
                if microsoft_department in restriction.bypass_department.split(','):
                    print(f"Restriction {type} bypassed for user {user_str} in department {microsoft_department}.")
                    return None
            if restriction.bypass_ip:
                if request.META['REMOTE_ADDR'] in restriction.bypass_ip.split(','):
                    print(f"Restriction {type} bypassed for user {user_str} with IP {request.META['REMOTE_ADDR']}.")
                    return None

            return restriction.message or ('Prihlasovanie je aktuálne obmedzené.' if type == 'login' else 'Registrácia je aktuálne obmedzená.')
        except AuthRestriction.DoesNotExist:
            print(f"Restriction {type} does not exist.")
            return None
        except:
            traceback.print_exc()
            return 'Nastala chyba pri povoľovaní prístupu.'

    def log_user_in(self, request, user, params):
        mode = params["mode"] if "mode" in params else "both"

        response_data = {
            "status": "success",
            "logged_user": UserSerializer(user).data
        }
        code = 200

        try:
            if mode == "direct":
                login(request, user)
            elif mode == "token":
                token_data = self.token_provider.create_token(request, user)
                response_data["user_token"] = token_data
            elif mode == "both":
                login(request, user)
                token_data = self.token_provider.create_token(request, user)
                response_data["user_token"] = token_data
            else:
                response_data = {
                    "status": "error",
                    "message": "Invalid value for parameter mode"
                }
                code = 400
        except Exception as e:
            traceback.print_exc()
            response_data = {
                "status": "error",
                "message": str(e)
            }
            code = 500

        return response_data, code

    def get_check_params(self, request, user=None, oauth_user=None, user_props=None):
        return {}

    def verify(self, request):
        # FE has authenticated user using OAuth, now we need to verify that login
        # because we can't trust FE as any data coming from there can be faked
        # (e.g. user_id, email, etc.)
        #
        # Exact verification process might differ based on the OAuth provider

        try:
            if self.oauth_user_model is not None:
                oauth_user = self.get_verification_oauth_user(request)
                try:
                    user = User.objects.get(**{self.user_property: oauth_user})
                except User.DoesNotExist:
                    restriction = self.check_restriction(request, 'register', **self.get_check_params(request, oauth_user=oauth_user))
                    if restriction is not None:
                        return Response({"status": "error", "message": f"STRERROR: {restriction}"}, 403)
                    user_props = self.get_verification_user_props(request, oauth_user)
                    if not self.user_property in user_props:
                        user_props[self.user_property] = oauth_user
                    user = User.objects.create(**user_props)
            else:
                user_props = self.get_verification_user_props(request)
                try:
                    user = User.objects.get(email=user_props["email"])
                except User.DoesNotExist:
                    restriction = self.check_restriction(request, 'register', **self.get_check_params(request, user_props=user_props))
                    if restriction is not None:
                        return Response({"status": "error", "message": f"STRERROR: {restriction}"}, 403)
                    user = User.objects.create(**user_props)

            restriction = self.check_restriction(request, 'login', user, **self.get_check_params(request, user=user))
            if restriction is not None:
                return Response({"status": "error", "message": f"STRERROR: {restriction}"}, 403)

            if not user.is_active:
                return Response({"status": "error", "message": f"STRERROR: Váš účet bol deaktivovaný"}, 403)

            response, status = self.log_user_in(request, user, request.GET.dict())
            return Response(response, status)
        except Exception as e:
            traceback.print_exc()
            return Response({"status": "error", "message": f"{e}"}, 500)