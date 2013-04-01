import calendar
import json
import pprint
import time
import uuid

from django import http
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

import commonware
import jwt

from inapp_pay_test.base.helpers import absolutify
from .decorators import post_required, json_view
from .models import Transaction, TRANS_PENDING

log = commonware.log.getLogger()


def home(request):
    iat = calendar.timegm(time.gmtime())
    exp = iat + 3600  # expires in 1 hour
    req = {
        'iss': settings.MOZ_APP_KEY,
        'aud': settings.MOZ_INAPP_AUD,
        'typ': settings.MOZ_INAPP_TYP,
        'exp': exp,
        'iat': iat,
        'request': {
            'pricePoint': 1,
            'id': str(uuid.uuid4()),
            'name': 'Virtual Kiwi',
            'icons': {
                '32': absolutify(settings.MEDIA_URL + 'img/kiwi_32.png'),
                '48': absolutify(settings.MEDIA_URL + 'img/kiwi_48.png'),
                '64': absolutify(settings.MEDIA_URL + 'img/kiwi_64.png'),
                '128': absolutify(settings.MEDIA_URL + 'img/kiwi_128.png'),
            },
            'description': 'the most delicious fruit on the Internet',
            'productData': '<this is not editable>',
            'chargebackURL': '<this is not editable>',
            'postbackURL': '<this is not editable>'
        }
    }
    if settings.SIMULATE:
        req['request']['simulate'] = settings.SIMULATE
    pay_request = json.dumps(req, indent=2)
    return render(request, 'app_payments/home.html',
                  {'pay_request': pay_request})


def manifest(request):
    resp = render(request, 'app_payments/manifest.webapp', {})
    resp['Content-Type'] = 'application/x-web-app-manifest+json'
    return resp


@post_required
# TODO(Kumar) figure out why csrf() isn't working. Even without csrf
# protection, users can still post arbitrary JSON from the form so csrf
# is not a big deal.
@csrf_exempt
@json_view
def sign_request(request):
    #
    # WARNING
    #
    # This is just a demo tool. You shouldn't ever sign a request
    # generated entirely from user input.
    #
    try:
        raw_pay_request = request.POST['pay_request']
        pay_request = {}
        trans = None
        try:
            pay_request = json.loads(raw_pay_request)
            trans = Transaction.objects.create(
                        state=TRANS_PENDING,
                        product=pay_request['request']['name'],
                        price_tier=pay_request['request']['pricePoint'],
                        description=pay_request['request']['description'])

            # Fix up the JWT.
            tx = 'transaction_id=%s' % trans.pk
            pay_request['request']['productData'] = tx
            cb = absolutify(reverse('app.mozmarket_chargeback'))
            pay_request['request']['chargebackURL'] = cb
            cb = absolutify(reverse('app.mozmarket_postback'))
            pay_request['request']['postbackURL'] = cb
        except:
            log.exception('Invalid JSON, ignoring')

        signed = jwt.encode(pay_request,
                            settings.MOZ_APP_SECRET, algorithm='HS256')
        return {'localTransID': trans and trans.pk,
                'signedRequest': signed}
    except:
        log.exception('in sign_request()')
        raise


@json_view
def check_trans(request):
    trans = get_object_or_404(Transaction, pk=request.GET.get('tx'))
    return {'localTransID': trans.pk,
            'mozTransactionID': trans.moz_transaction_id,
            'transState': trans.state}


def show_settings(request):
    whitelist = ('LOGGING',)
    vals = [(k, getattr(settings, k)) for k in dir(settings)
            if k in whitelist]
    return http.HttpResponse(pprint.pformat(dict(vals)),
                             content_type='text/plain')
