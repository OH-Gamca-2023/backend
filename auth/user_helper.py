from datetime import timedelta

from django.contrib.auth import login
from django.utils import timezone
from django.utils.crypto import get_random_string

from users.models import MicrosoftUser, User, UserToken


def handle_user_login(request, user):
    id = user['id']
    if not MicrosoftUser.objects.filter(id=id).exists():
        MicrosoftUser.objects.create(
            id=id,
            mail=user['mail'],
            display_name=user['displayName'],
            given_name=user['givenName'],
            surname=user['surname'],
            job_title=user['jobTitle'],
            office_location=user['officeLocation'],
            department=user['department'],
        )

    msft_user = MicrosoftUser.objects.get(id=id)
    if not User.objects.filter(microsoft_user=msft_user).exists():
        user_clazz = msft_user.get_clazz()

        User.objects.create(
            microsoft_user=msft_user,
            clazz=user_clazz,

            username=f"{msft_user.given_name} {msft_user.surname}",
            email=msft_user.mail,

            first_name=msft_user.given_name,
            last_name=msft_user.surname,

            is_active=True,
            is_staff=user_clazz.grade.name == 'Organizátori',
            is_superuser=False,
        )

    django_user = User.objects.get(microsoft_user=msft_user)

    return django_user


def create_user_token(request, user):
    token_string = get_random_string(length=64)
    expiry_date = timezone.now() + timedelta(days=7)

    token = UserToken.objects.create(
        token=token_string,
        user=user,
        expires=expiry_date,
    )

    return token
