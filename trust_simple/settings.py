import os
from os import environ

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = 'replace-this-with-your-secret-key'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = []

SESSION_CONFIG_DEFAULTS = {
    'real_world_currency_per_point': 1.00,
    'participation_fee': 0.00,
    'doc': "",
}

SESSION_CONFIGS = [
    dict(
        name='feedback_study',
        display_name="Feedback Study",
        app_sequence=['trust_tutorial', 'final_save'],
        num_demo_participants=10,
    ),
]

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False  # False to not round, puts it into money

INSTALLED_APPS = ['otree']

STATIC_URL = '/static/'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
