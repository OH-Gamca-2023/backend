# Profile edit permission - specifies which fields can be edited by which users
profile_edit_permission = {
    'student': ['phone_number', 'email'],
    'alumni': ['phone_number', 'email'],
    'teacher': ['phone_number', 'email'],
    'organiser': ['phone_number', 'email', 'username', 'password'],
    'admin': ['first_name', 'last_name', 'phone_number', 'email', 'username', 'password'],
}
