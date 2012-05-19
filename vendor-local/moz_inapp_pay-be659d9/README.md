Python module to work with Mozilla Marketplace in-app payments.

You can read all about how in-app payments work in the
[developer docs](https://developer.mozilla.org/en/Apps/In-app_payments).

Mozilla's in-app payments allow you to operate an app that accepts
payments for digital goods. As payments are completed, the Mozilla Marketplace
needs to communicate the transaction ID to your app. You can use this library to
validate the signature of that communication.

Installation
============

With [pip](http://www.pip-installer.org/) or easy_install, run:

    pip install moz_inapp_pay

Or install it from source (recommended):

    pip install git+git://github.com/kumar303/moz_inapp_pay.git

Verify a postback
=================

    import logging
    from moz_inapp_pay import InvalidJWT, process_postback
    try:
        data = process_postback(signed_request,
                                app_key,
                                app_secret)
        print data['response']['transactionID']
    except InvalidJWT:
        loggging.exception('in postback')


Verify a chargeback
===================

    import logging
    from moz_inapp_pay import InvalidJWT, process_chargeback
    try:
        data = process_chargeback(signed_request,
                                  app_key,
                                  app_secret)
        print data['response']['transactionID']
        print data['response']['reason']
    except InvalidJWT:
        logging.exception('in chargeback')


Use It With Django
==================

If you use the [Django](https://www.djangoproject.com/) framework,
there's an app you can plug right into your urls.py.

Add the app in your settings.py file:

    INSTALLED_APPS = [
        # ...
        'moz_inapp_pay.djangoapp',
    ]

Add your key and secret that was granted by the Mozilla Marketplace to your
**local** settings.py file:

    MOZ_APP_KEY = '<from marketplace.mozilla.org>'
    MOZ_APP_SECRET = '<from marketplace.mozilla.org>'

**Do not commit your secret to a public repo. Always keep it secure on your
server**

Add the postback / chargeback URLs to your urls.py file:

    from django.conf.urls.defaults import patterns, include

    urlpatterns = patterns('',
        ('^moz/', include('moz_inapp_pay.djangoapp.urls')),
    )

This will add ``/moz/postback`` and ``/moz/chargeback`` to your URLs.
You'll enter these callback URLs into the in-app payment config screen on the
Mozilla Marketplace.

If you want to do further processing on the postbacks, you can connect to a
few signals. Here is an example of code to go in your app
(probably in models.py):

    import logging
    from django.dispatch import receiver

    from moz_inapp_pay.djangoapp.signals import (moz_inapp_postback,
                                                 moz_inapp_chargeback)


    @receiver(moz_inapp_postback)
    def mozmarket_postback(request, jwt_data, **kwargs):
        logging.info('transaction ID %s processed ok'
                     % jwt_data['response']['transactionID'])


    @receiver(moz_inapp_chargeback)
    def mozmarket_chargeback(request, jwt_data, **kwargs):
        logging.info('transaction ID %s charged back; reason: %r'
                     % (jwt_data['response']['transactionID'],
                        jwt_data['response']['reason']))


Exceptions are logged to the channel ``moz_inapp_pay.djangoapp.views``
so be sure to add the appropriate handlers to that.

When an InvalidJWT exception occurs, a 400 Bad Request is returned.
