import calendar
import json
import time
import urlparse

from django import http
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

import commonware
import jwt

from .decorators import post_required, json_view
from .models import Transaction, TRANS_PENDING, TRANS_DONE

log = commonware.log.getLogger()


def home(request):
    iat = calendar.timegm(time.gmtime())
    exp = iat + 3600  # expires in 1 hour
    pay_request = json.dumps({
        'iss': settings.APPLICATION_KEY,
        'aud': 'marketplace.mozilla.org',
        'typ': 'mozilla/payments/pay/v1',
        'exp': exp,
        'iat': iat,
        'request': {
            'price': '0.99',
            'currency': 'USD',
            'name': 'The Product',
            'description': 'detailed description',
            'productdata': '<set to local transaction ID>'
        }
    }, indent=2)
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
        pay_request = trans = None
        try:
            pay_request = json.loads(raw_pay_request)
            trans = Transaction.objects.create(
                        state=TRANS_PENDING,
                        product=pay_request['request']['name'],
                        price=pay_request['request']['price'],
                        currency=pay_request['request']['currency'],
                        description=pay_request['request']['description'])
            tx = 'transaction_id=%s' % trans.pk
            pay_request['request']['productdata'] = tx
            raw_pay_request = json.dumps(pay_request)
        except (ValueError, KeyError):
            log.exception('Invalid JSON, ignoring')

        signed = jwt.encode(raw_pay_request,
                            settings.APPLICATION_SECRET, algorithm='HS256')
        return {'localTransID': trans and trans.pk,
                'signedRequest': signed}
    except:
        log.exception('in sign_request()')
        raise


@post_required
@csrf_exempt
def mozmarket_postback(request):
    try:
        payload = request.read()
        data = jwt.decode(payload, verify=False)
        log.info('Got postback payload: %s' % data)
        jwt.decode(payload, settings.APPLICATION_SECRET, verify=True)
        moz_trans_id = data['response']['transactionID']

        # e.g. transaction_id=1234
        pd = urlparse.parse_qs(data['request']['productdata'])
        trans = Transaction.objects.get(pk=pd['transaction_id'][0])
        trans.moz_transaction_id = moz_trans_id
        trans.state = TRANS_DONE
        trans.save()

        log.info('signature verified; responding with %s' % moz_trans_id)
        return http.HttpResponse(str(moz_trans_id))
    except:
        log.exception('Exception while processing request from %s'
                      % request.META.get('REMOTE_ADDR'))
        raise


@csrf_exempt
def mozmarket_chargeback(request):
    pass


@json_view
def check_trans(request):
    trans = get_object_or_404(Transaction, pk=request.GET.get('tx'))
    return {'localTransID': trans.pk,
            'mozTransactionID': trans.moz_transaction_id}
