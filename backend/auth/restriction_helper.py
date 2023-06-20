from data.models import AuthRestriction


def is_allowed(request, type, user=None, department=None):
    if type not in ['register', 'login']:
        raise Exception('Invalid type.')

    try:
        restriction = AuthRestriction.objects.get(type=type)
        if not restriction.restricted:
            return True, ""

        if user:
            if restriction.bypass_staff and user.is_staff:
                return True, f"Restriction {type} bypassed for staff user [{user.username}#{user.id}]."
            if restriction.bypass_superuser and user.is_superuser:
                return True, f"Restriction {type} bypassed for superuser [{user.username}#{user.id}]."
        if department:
            if department in restriction.bypass_department.split(','):
                return True, f"Restriction {type} bypassed for user [{user.username}#{user.id}] in department {department}."
        if restriction.bypass_ip:
            if request.META['REMOTE_ADDR'] in restriction.bypass_ip.split(','):
                return True, f"Restriction {type} bypassed for user [{user.username}#{user.id}] with IP {request.META['REMOTE_ADDR']}."

        return False, restriction.message
    except AuthRestriction.DoesNotExist:
        return True, f"Restriction {type} does not exist."
    except Exception as e:
        print(e)
        return False, 'Nastala chyba pri overovaní prihlasovania.'
