# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py

from funfactory.settings_base import *
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(__file__), 'inapp_pay_test.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {},
        'TEST_CHARSET': 'utf8',
        'TEST_COLLATION': 'utf8_general_ci',
    },
}

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'example_css': (
            'css/examples/main.css',
        ),
        'example_mobile_css': (
            'css/examples/mobile.css',
        ),
        'app_payments': (
            'css/app_payments/base.css',
        ),
    },
    'js': {
        'example_js': (
            'js/examples/libs/jquery-1.4.4.min.js',
            'js/examples/libs/jquery.cookie.js',
            'js/examples/init.js',
        ),
        'app_payments': (
            'js/libs/jquery-1.4.4.min.js',
            'js/app_payments.js',
        ),
    }
}

# Defines the views served for root URLs.
ROOT_URLCONF = 'inapp_pay_test.urls'

INSTALLED_APPS = list(INSTALLED_APPS) + [
    # Application base, containing global templates.
    'inapp_pay_test.base',
    'inapp_pay_test.app_payments',

    'django.contrib.admin',
]


# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
]

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['lhtml'] = [
#    ('**/templates/**.lhtml',
#        'tower.management.commands.extract.extract_tower_template'),
# ]

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['javascript'] = [
#    # Make sure that this won't pull in strings from external libraries you
#    # may use.
#    ('media/js/**.js', 'javascript'),
# ]

LOGGIN = {'loggers': {'playdoh': {'level': logging.DEBUG}}}

# URL to the JS file for the app to include to make in-app payments.
# By default this is the local reference implementation.
INAPP_PAYMENTS_JS = 'https://marketplace-dev-cdn.allizom.org/media/js/mozmarket.js'

# After registering an app for in-app payments
# on https://marketplace.mozilla.org/
# fill these in from the Manage In-app Payments screen.
#
# set these in settings/local.py
#
# **DO NOT** commit your app secret to github :)
#
APPLICATION_KEY = '<from marketplace.mozilla.org>'
APPLICATION_SECRET = '<from marketplace.mozilla.org>'
