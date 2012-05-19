import calendar
from datetime import datetime, timedelta
import json
import time
import unittest

import jwt
from nose.tools import eq_, raises

import moz_inapp_pay
from moz_inapp_pay.exc import InvalidJWT, RequestExpired

from . import JWTtester


class TestVerify(JWTtester):

    def setUp(self):
        super(TestVerify, self).setUp()
        self.verifier = moz_inapp_pay.process_postback

    @raises(InvalidJWT)
    def test_unknown_secret(self):
        self.verify(self.request(app_secret='invalid'))

    @raises(InvalidJWT)
    def test_garbage_request(self):
        self.verify('<not valid JWT>')

    @raises(InvalidJWT)
    def test_non_ascii_jwt(self):
        self.verify(u'Ivan Krsti\u0107 is in your JWT')

    @raises(InvalidJWT)
    def test_mangled_json(self):
        encoded = self.request(payload='[\\}()')  # json syntax error
        self.verify(encoded)

    @raises(RequestExpired)
    def test_expired(self):
        now = calendar.timegm(time.gmtime())
        old = datetime.utcfromtimestamp(now) - timedelta(minutes=1)
        exp = calendar.timegm(old.timetuple())
        self.verify(self.request(exp=exp))

    @raises(RequestExpired)
    def test_expired_iat(self):
        old = calendar.timegm(time.gmtime()) - 3660  # 1hr, 1min ago
        self.verify(self.request(iat=old))

    @raises(InvalidJWT)
    def test_invalid_expiry(self):
        self.verify(self.request(exp='<not a number>'))

    @raises(InvalidJWT)
    def test_invalid_expiry_non_ascii(self):
        self.verify(update={'exp': u'Ivan Krsti\u0107 is in your JWT'})

    @raises(InvalidJWT)
    def test_none_expiry(self):
        self.verify(update={'exp': None})

    @raises(InvalidJWT)
    def test_invalid_iat_non_ascii(self):
        self.verify(update={'iat': u'Ivan Krsti\u0107 is in your JWT'})

    @raises(InvalidJWT)
    def test_none_iat(self):
        self.verify(update={'iat': None})

    @raises(InvalidJWT)
    def test_not_before(self):
        nbf = calendar.timegm(time.gmtime()) + 310  # 5:10 in the future
        self.verify(update={'nbf': nbf})

    def test_ignore_invalid_nbf(self):
        data = self.verify(update={'nbf': '<garbage>'})
        eq_(data['nbf'], None)

    @raises(InvalidJWT)
    def test_require_iss(self):
        payload = self.payload()
        del payload['iss']
        self.verify(self.request(payload=json.dumps(payload)))

    @raises(InvalidJWT)
    def test_require_price(self):
        payload = self.payload()
        del payload['request']['price']
        self.verify(self.request(payload=json.dumps(payload)))

    @raises(InvalidJWT)
    def test_require_currency(self):
        payload = self.payload()
        del payload['request']['currency']
        self.verify(self.request(payload=json.dumps(payload)))

    @raises(InvalidJWT)
    def test_require_name(self):
        payload = self.payload()
        del payload['request']['name']
        self.verify(self.request(payload=json.dumps(payload)))

    @raises(InvalidJWT)
    def test_require_description(self):
        payload = self.payload()
        del payload['request']['description']
        self.verify(self.request(payload=json.dumps(payload)))

    @raises(InvalidJWT)
    def test_require_request(self):
        payload = self.payload()
        del payload['request']
        self.verify(self.request(payload=json.dumps(payload)))

    @raises(InvalidJWT)
    def test_require_response(self):
        payload = self.payload()
        del payload['response']
        self.verify(self.request(payload=json.dumps(payload)))

    @raises(InvalidJWT)
    def test_require_transaction_id(self):
        payload = self.payload()
        del payload['response']['transactionID']
        self.verify(self.request(payload=json.dumps(payload)))

    @raises(InvalidJWT)
    def test_invalid_audience(self):
        self.verify(update={'aud': 'not my app'})

    @raises(InvalidJWT)
    def test_missing_audience(self):
        payload = self.payload()
        del payload['aud']
        self.verify(self.request(payload=json.dumps(payload)))

    @raises(InvalidJWT)
    def test_malformed_jwt(self):
        self.verify(self.request() + 'x')
