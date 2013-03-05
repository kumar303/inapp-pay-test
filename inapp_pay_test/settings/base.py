# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py

import json
import os
from funfactory.settings_base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(ROOT, 'inapp_pay_test.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {},
        'TEST_CHARSET': 'utf8',
        'TEST_COLLATION': 'utf8_general_ci',
    },
}

if os.environ.get('VCAP_APPLICATION'):
    VCAP_APP = json.loads(os.environ['VCAP_APPLICATION'])
else:
    VCAP_APP = None

# True if we running as a Stackato instance.
STACKATO = bool(VCAP_APP)

# This must match what you see in your URL bar when you run the website.
# TODO(Kumar): check for https?
SITE_URL = ('http://%s' % VCAP_APP['uris'][0] if VCAP_APP
            else 'http://localhost:8000')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

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

# jingo-minify: Style sheet media attribute default
CSS_MEDIA_DEFAULT = 'all'

# Tell jingo-minify to use the media URL instead.
JINGO_MINIFY_USE_STATIC = False

# LESS CSS OPTIONS (Debug only)
LESS_PREPROCESS = False  # Compile LESS with Node, rather than client-side JS?
LESS_LIVE_REFRESH = False  # Refresh the CSS on save?
LESS_BIN = 'lessc'
UGLIFY_BIN = 'uglifyjs'
CLEANCSS_BIN = 'cleancss'

# Defines the views served for root URLs.
ROOT_URLCONF = 'inapp_pay_test.urls'

INSTALLED_APPS = list(INSTALLED_APPS) + [
    # Application base, containing global templates.
    'inapp_pay_test.base',
    'inapp_pay_test.app_payments',
    'moz_inapp_pay.djangoapp',

    'django.contrib.admin',
]

MIDDLEWARE_CLASSES = (
    'inapp_pay_test.base.middleware.LocaleMiddleware',
    'multidb.middleware.PinningRouterMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',  # Must be after auth middleware.
    'django.contrib.messages.middleware.MessageMiddleware',
    'commonware.middleware.FrameOptionsHeader',
    'mobility.middleware.DetectMobileMiddleware',
    'mobility.middleware.XMobileMiddleware',
    'inapp_pay_test.base.middleware.LogExceptionsMiddleware'
)


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

# Paths that don't require a locale code in the URL.
SUPPORTED_NONLOCALES = [
    'media',
    'admin',
    'manifest.webapp',
    'postback',
    'chargeback',
]

LOGGING = {'loggers': {'playdoh': {'level': logging.INFO,
                                   'handlers': ['console']},
                       'moz_inapp_pay': {'level': logging.DEBUG,
                                         'handlers': ['console'],
                                         'propagate': True},
                       # Root logger.
                       '': {'level': logging.INFO,
                            'handlers': ['console']}}}

# URL to the JS file for the app to include to make in-app payments.
# By default this is the local reference implementation.
INAPP_PAYMENTS_JS = 'https://marketplace-dev-cdn.allizom.org/mozmarket.js'

# After registering an app for in-app payments
# on https://marketplace.mozilla.org/
# fill these in from the Manage In-app Payments screen.
#
# set these in settings/local.py
#
# **DO NOT** commit your app secret to github :)
#
MOZ_APP_KEY = '<from marketplace.mozilla.org>'
MOZ_APP_SECRET = '<from marketplace.mozilla.org>'
# The audience of the JWT.
MOZ_INAPP_AUD = 'firefox.marketplace.com'
MOZ_INAPP_TYP = 'mozilla/payments/pay/v1'

if STACKATO:
    # Currently, Mozilla's Stackato only has a self-signed https cert.
    # TODO: fix this when we have https support.
    SESSION_COOKIE_SECURE = False
    # TODO: remove this when we have a way to see exceptions on Stackato.
    DEBUG = TEMPLATE_DEBUG = True
