from django.contrib.auth import authenticate
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication


class CredentialsAuthentication(BaseAuthentication):
    def authenticate(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        if username is None and email is None or password is None:
            return None
        if username is not None and email is not None:
            raise exceptions.AuthenticationFailed('Only one of username or email can be provided at the same time')
        user = authenticate(username=username, email=email, password=password)
        if user is None:
            raise exceptions.AuthenticationFailed('Invalid credentials')
        return user, None
