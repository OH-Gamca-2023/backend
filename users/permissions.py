# all permissions are treated as regexes
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
    'kalendar\\.delete_calendar',
]

# Blacklist - permissions that are not allowed to be assigned to users
# can be overriden by assigning them to a user or a group directly
blacklist = [
    # prevent tampering with user tokens
    'users\\.add_usertoken',
    'users\\.change_usertoken',
    'users\\.delete_usertoken',
]

# Admin - permissions that admins have by default
admin = [
    'users\\.(.*)',
    'kalendar\\.(.*)',
]

# Organizer - permissions that organizers have by default
organizer = []

# Default - permissions that all users (students, alumni, teachers) have by default
default = []


default_module_permissions = set(map(lambda x: x.split('.')[0], default))
organizer_module_permissions = set(map(lambda x: x.split('.')[0], default + organizer))
admin_module_permissions = set(map(lambda x: x.split('.')[0], default + organizer + admin))


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
