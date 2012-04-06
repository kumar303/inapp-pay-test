from django.conf.urls.defaults import *

from . import views


urlpatterns = patterns('',
    url(r'^$', views.home, name='app_payments.home'),
    url(r'^sign-request$', views.sign_request,
        name='app_payments.sign_request'),
    url(r'^manifest\.webapp$', views.manifest, name='app_payments.manifest'),
    url(r'^check-trans$', views.check_trans, name='app.check_trans'),
    url(r'^postback$', views.mozmarket_postback,
        name='app.mozmarket_postback'),
    url(r'^chargeback$', views.mozmarket_chargeback,
        name='app.mozmarket_chargeback'),
)
