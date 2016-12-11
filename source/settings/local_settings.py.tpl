# coding: utf-8

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your db name',
        'USER': 'your db user',
        'PASSWORD': 'your db password',
        'HOST': 'mysql',
        'PORT': '3306',
    }
}

RAVEN_CONFIG = {}
