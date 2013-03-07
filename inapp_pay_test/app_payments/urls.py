from django.conf.urls.defaults import *

from mozpay.djangoapp import views as moz_views

from funfactory.monkeypatches import patch
patch()

from . import views


urlpatterns = patterns('',
    url(r'^$', views.home, name='app_payments.home'),
    url(r'^sign-request$', views.sign_request,
        name='app_payments.sign_request'),
    url(r'^manifest\.webapp$', views.manifest, name='app_payments.manifest'),
    url(r'^check-trans$', views.check_trans, name='app.check_trans'),
    url(r'^settings$', views.show_settings,
        name='app.show_settings'),

    # Moz in-app payment postbacks:
    url(r'^postback$', moz_views.postback,
        name='app.mozmarket_postback'),
    url(r'^chargeback$', moz_views.chargeback,
        name='app.mozmarket_chargeback'),
)
