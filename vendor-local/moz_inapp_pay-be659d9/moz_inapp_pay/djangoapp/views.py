import logging

from django import http
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import moz_inapp_pay
from moz_inapp_pay import InvalidJWT
from . import signals

log = logging.getLogger(__name__)


@require_POST
@csrf_exempt
def postback(request):
    try:
        data = moz_inapp_pay.process_postback(request.read(),
                                              settings.MOZ_APP_KEY,
                                              settings.MOZ_APP_SECRET)
    except InvalidJWT:
        log.exception('in postback')
        return http.HttpResponseBadRequest()
    signals.moz_inapp_postback.send(sender=None, jwt_data=data,
                                    request=request)
    return http.HttpResponse(str(data['response']['transactionID']))


@require_POST
@csrf_exempt
def chargeback(request):
    try:
        data = moz_inapp_pay.process_chargeback(request.read(),
                                                settings.MOZ_APP_KEY,
                                                settings.MOZ_APP_SECRET)
    except InvalidJWT:
        log.exception('in chargeback')
        return http.HttpResponseBadRequest()
    signals.moz_inapp_chargeback.send(sender=None, jwt_data=data,
                                      request=request)
    return http.HttpResponse(str(data['response']['transactionID']))
