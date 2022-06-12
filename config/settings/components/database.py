from config.settings.components import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', '127.0.0.1'),
        'PORT': config('DB_PORT', 5432),
        'OPTIONS': {
            'options': '-c search_path=public,content',
        },
    },
}

CONN_MAX_AGE = 10
