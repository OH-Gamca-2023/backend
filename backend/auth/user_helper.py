from backend.auth.restriction_helper import is_allowed
from backend.users.models import MicrosoftUser, User, Clazz, Grade


def handle_user_login(request, user, admin=False):
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
    else:
        # check if all information is up to date and update if necessary
        msft_user = MicrosoftUser.objects.get(id=id)
        changed = False
        for key in ['mail', 'display_Name', 'given_Name', 'surname', 'job_Title', 'office_Location', 'department']:
            key1, key2 = key.lower(), key.replace('_', '')
            if getattr(msft_user, key1) != user[key2]:
                setattr(msft_user, key1, user[key2])
                changed = True
        if changed:
            msft_user.save()
        
    msft_user = MicrosoftUser.objects.get(id=id)
    if not User.objects.filter(microsoft_user=msft_user).exists():
        allowed, message = is_allowed(request, 'register', None, msft_user.department)
        if not allowed:
            raise Exception(f'STRERROR: {message}')
        if allowed and message != "":
            print(message)
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

    allowed, message = is_allowed(request, 'login', User.objects.get(microsoft_user=msft_user), msft_user.department)
    if not allowed:
        raise Exception(f'STRERROR: {message}')
    if allowed and message != "":
        print(message)

    django_user = User.objects.get(microsoft_user=msft_user)

    if admin:
        if not django_user.is_staff:
            raise Exception('STRERROR: Not an admin')

    return django_user


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
