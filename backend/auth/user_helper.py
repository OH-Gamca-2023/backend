from datetime import timedelta

from django.utils import timezone
from django.utils.crypto import get_random_string

from backend.users.models import MicrosoftUser, User, UserToken, Clazz, Grade


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
        user_clazz = process_clazz(msft_user)
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


MAX_TOKENS_PER_USER = 5


def create_user_token(request, user):
    token_string = get_random_string(length=64)
    expiry_date = timezone.now() + timedelta(days=7)

    tokens = UserToken.objects.filter(user=user, invalid=False, expires__gt=timezone.now()).order_by('-created')
    print(tokens.count(), tokens)
    if tokens.count() >= MAX_TOKENS_PER_USER:
        last_token = tokens.last()
        last_token.invalid = True
        last_token.save()

    token = UserToken.objects.create(
        token=token_string,
        user=user,
        expires=expiry_date,
    )

    return token


def process_clazz(msft_user):
    if msft_user.get_clazz() is not None:
        return msft_user.get_clazz()
    else:
        if msft_user.department == 'alumni':
            return Clazz.objects.create(
                name='Alumni',
                grade=Grade.objects.get(name='Alumni'),
                is_fake=True,
                microsoft_department='alumni'
            )
        elif msft_user.department == 'zamestnanci':
            return Clazz.objects.create(
                name='Učitelia',
                grade=Grade.objects.get(name='Učitelia'),
                is_fake=True,
                microsoft_department='zamestnanci'
            )
        else:
            if '.' in msft_user.department:
                year, clazz = msft_user.department.split('.')
                return Clazz.objects.create(
                    name=year+". "+clazz,
                    grade=Grade.objects.get(name="3. Stupeň"),
                    is_fake=False,
                    microsoft_department=msft_user.department
                )
            else:
                clazz = msft_user.department

                grade = Grade.objects.get(name="3. Stupeň")
                if clazz[:-1] in ['Prima', 'Sekunda', 'Tercia', 'Kvarta']:
                    grade = Grade.objects.get(name="2. Stupeň")

                if clazz[-1] == 'A' or clazz[-1] == 'B':
                    clazz = clazz[:-1] + ' ' + clazz[-1]

                return Clazz.objects.create(
                    name=clazz,
                    grade=grade,
                    is_fake=False,
                    microsoft_department=msft_user.department
                )
