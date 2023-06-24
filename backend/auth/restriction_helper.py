import traceback

from backend.data.models import AuthRestriction


def is_allowed(request, type, user=None, department=None):
    if type not in ['register', 'login']:
        raise Exception('Invalid type.')

    try:
        restriction = AuthRestriction.objects.get(type=type)
        if not restriction.restricted:
            return True, ""

        user_str = f"[{user.username}#{user.id}]" if user else "[anon]"

        if user:
            if restriction.bypass_staff and user.is_staff:
                return True, f"Restriction {type} bypassed for staff user {user_str}."
            if restriction.bypass_superuser and user.is_superuser:
                return True, f"Restriction {type} bypassed for superuser {user_str}."
        if department:
            if department in restriction.bypass_department.split(','):
                return True, f"Restriction {type} bypassed for user {user_str} in department {department}."
        if restriction.bypass_ip:
            if request.META['REMOTE_ADDR'] in restriction.bypass_ip.split(','):
                return True, f"Restriction {type} bypassed for user {user_str} with IP {request.META['REMOTE_ADDR']}."

        return False, restriction.message
    except AuthRestriction.DoesNotExist:
        return True, f"Restriction {type} does not exist."
    except:
        traceback.print_exc()
        return False, 'Nastala chyba pri povoľovaní prístupu.'
