# all permissions are treated as regexes
# as module splitter always use \\. (otherwise module permissions will not work)
#
# please use comments to explain why each permission or group of permissions is used
# can be omitted if the permission is self-explanatory
import re

# Force blacklist - permissions that are not allowed to be assigned to users
# overrides everything else
force_blacklist = [
    # prevent modifying unwanted kalendar models
    'kalendar\\.change_(.*)',
    'kalendar\\.delete_generationevent',
    'kalendar\\.add_generationevent',
    'data\\.delete_authrestriction',
]

# Blacklist - permissions that are not allowed to be assigned to users
# can be overriden by assigning them to a user or a group directly
blacklist = [
    # prevent removing calendars and settings for everyone but superusers
    'kalendar\\.delete_calendar',
    'data\\.delete_(.*)',
    # prevent unwanted user modifications
    'users\\.delete_microsoftuser',
    'users\\.delete_user',
    'users\\.delete_grade',
]

# Admin - permissions that admins have by default
admin = [
    'disciplines\\.(.*)',
    'posts\\.(.*)',
    'users\\.(.*)',
    'kalendar\\.(.*)',
    'data\\.(.*)',
    'ciphers\\.(.*)',
    'knox\\.view_authtoken',
    'admin\\.view_logentry',
]

# Organizer - permissions that organizers have by default
organizer = [
    'disciplines\\.(.*)_discipline',
    'disciplines\\.view_category',
    'disciplines\\.(.*)_result',
    'disciplines\\.publish_details',
    'disciplines\\.publish_results',
    'disciplines\\.(.*)_placements',
    'posts\\.(.*)_post',
    'posts\\.(view|add)_comment',
    'posts\\.(view|add)_tag',
    'ciphers\\.(.*)_cipher',
    'ciphers\\.(view)_submission',
    'users\\.view_grade',
    'users\\.view_clazz',
]

# Default - permissions that all users (students, alumni, teachers) have by default
default = []


default_module_permissions = set(map(lambda x: x.split('\\.')[0], default))
organizer_module_permissions = set(map(lambda x: x.split('\\.')[0], default + organizer))
admin_module_permissions = set(map(lambda x: x.split('\\.')[0], default + organizer + admin))


def matches(p_set, permission):
    return any(re.match(regex, permission) for regex in p_set)


# Permissions are checked in order:
# 1. force_blacklist - deny if matches
# 2. direct user/group assignment - allow if matches
#   2.1. superuser - allow everything
# 3. blacklist - deny if matches
# 4. admin (if user is admin) - allow if matches
# 5. organizer (if user is organizer or admin) - allow if matches
# 6. default - allow if matches

# Profile edit permission - specifies which fields can be edited by which users
profile_edit_permission = {
    'student': [],
    'alumni': ['email'],
    'teacher': ['email'],
    'organizer': ['email', 'username', 'password'],
    'admin': ['first_name', 'last_name', 'email', 'username', 'password'],
}
