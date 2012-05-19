from django.conf.urls.defaults import *

from . import views


urlpatterns = patterns('',
    url(r'^postback$', views.postback,
        name='moz_inapp_pay.postback'),
    url(r'^chargeback$', views.chargeback,
        name='moz_inapp_pay.chargeback'),
)
