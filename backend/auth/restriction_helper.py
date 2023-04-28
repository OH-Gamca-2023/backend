from data.models import AuthRestriction


def is_allowed(request, type, user=None, department=None):
    if type not in ['registration', 'login']:
        raise Exception('Invalid type.')

    try:
        restriction = AuthRestriction.objects.get(type=type)
        if not restriction.restricted:
            return True, ""

        if user:
            if restriction.bypass_staff and user.is_staff:
                return True, ""
            if restriction.bypass_admin and user.is_admin:
                return True, ""
            if restriction.bypass_superuser and user.is_superuser:
                return True, ""
        if department:
            if department in restriction.bypass_department.split(','):
                return True, ""
        if restriction.bypass_ip:
            if request.META['REMOTE_ADDR'] in restriction.bypass_ip.split(','):
                return True, ""

        return False, restriction.message
    except AuthRestriction.DoesNotExist:
        return (True, )
    except Exception as e:
        print(e)
        return False, 'Nastala chyba pri overovaní prihlasovania.'
