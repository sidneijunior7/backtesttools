def users():
    credentials = {
        'usernames': {
            'sidneijunior': {
                'name': 'Junior',
                'password': ('sssj170795'),  # Aplicando hash aqui
                'email' : 'sidneijunior@icloud.com'
            },
            'user1': {
                'name': 'User One',
                'password': ('password1'),
                'email' : ''
            }
        }
    }

    return credentials
